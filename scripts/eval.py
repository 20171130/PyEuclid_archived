#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import json
import math
import copy
import random
import traceback
import argparse
import signal
import multiprocessing as mp
from pathlib import Path
from typing import Optional, Union, List, Tuple, Dict, Any, Iterable, Set, Callable

from stopit import ThreadingTimeout as TT
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps

import pyeuclid.formalization.utils as utils
from pyeuclid.formalization.state import State
from pyeuclid.formalization.translation import (
    parse_texts_from_file,
    parse_construction_program,
)
from pyeuclid.formalization.construction_rule import *
from pyeuclid.formalization.relation import *
from pyeuclid.engine.deductive_database import DeductiveDatabase
from pyeuclid.engine.algebraic_system import AlgebraicSystem
from pyeuclid.engine.proof_generator import ProofGenerator
from pyeuclid.engine.engine import Engine

from openai import OpenAI, AzureOpenAI
import google.generativeai as genai
import google.api_core.exceptions


# =======================
# Helpers
# =======================

def backoff(
    tries: int = 3,
    base: float = 0.5,
    factor: float = 2.0,
    exceptions: Tuple[type, ...] = (Exception,),
):
    """Simple exponential backoff decorator."""
    def deco(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            delay = base
            last_exc = None
            for i in range(tries):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if i == tries - 1:
                        break
                    time.sleep(delay)
                    delay *= factor
            if last_exc:
                raise last_exc
        return wrapper
    return deco


def get_array_info() -> Tuple[int, int]:
    """Cooperate with SLURM arrays, but stay robust if unset."""
    tid = int(os.environ.get("SLURM_ARRAY_TASK_ID", "0"))
    tcount = int(os.environ.get("SLURM_ARRAY_TASK_COUNT", "1"))
    return tid, max(1, tcount)


def is_my_index(idx: int, task_id: int, task_count: int) -> bool:
    return (idx % task_count) == task_id


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def write_text_atomic(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def write_json_atomic(path: Path, payload: Any) -> None:
    write_text_atomic(path, json.dumps(payload, indent=2, ensure_ascii=False))


def normalize_one_line(s: str) -> str:
    """
    Normalize any model output into ONE comma-separated line:
    - strip whitespace
    - split on newlines/semicolons
    - collapse repeated commas/spaces
    - remove trailing commas
    """
    if not s:
        return ""
    parts = []
    for chunk in s.replace(";", "\n").splitlines():
        chunk = chunk.strip().strip(",")
        if chunk:
            parts.append(chunk)
    if not parts:
        return ""
    joined = ", ".join(parts)
    joined = ", ".join([p.strip().strip(",") for p in joined.split(",") if p.strip().strip(",")])
    return joined


def uniq(iterable: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    out: List[str] = []
    for x in iterable:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out


def normalize_score(score: Optional[float]) -> float:
    """Higher is better. If score is None or NaN, treat as 0.0."""
    try:
        if score is None or math.isnan(float(score)):
            return 0.0
        return float(score)
    except Exception:
        return 0.0


# =======================
# Providers
# =======================

class GeminiProvider:
    """
    Google Gemini API wrapper with token logprobs enabled.
    - Uses generation_config={"response_logprobs": True} (no explicit top-K).
    - Caps candidate_count at 8 per request (Gemini limit).
    - Extracts average chosen-token logprob from candidate attributes.
    Returns: List[(text, avg_logprob_or_None)]
    """

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        if not api_key:
            raise RuntimeError("Gemini API key is required.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name=model)

    @classmethod
    def _average_logprob_from_candidate(cls, cand) -> Optional[float]:
        try:
            if hasattr(cand, 'logprobs_result'):
                logprobs_result = getattr(cand, 'logprobs_result')
                if logprobs_result and hasattr(logprobs_result, 'chosen_candidates'):
                    chosen_candidates = logprobs_result.chosen_candidates
                    if chosen_candidates:
                        log_probs = []
                        for token_info in chosen_candidates:
                            if hasattr(token_info, 'log_probability'):
                                log_probs.append(float(token_info.log_probability))
                        if log_probs:
                            return sum(log_probs) / len(log_probs)
            if hasattr(cand, 'avg_logprobs'):
                avg_logprobs = getattr(cand, 'avg_logprobs')
                if avg_logprobs is not None and avg_logprobs != 0.0:
                    return float(avg_logprobs)
            return None
        except Exception:
            return None

    @backoff(tries=3, base=0.5, factor=2.0,
             exceptions=(google.api_core.exceptions.GoogleAPICallError, RuntimeError))
    def _single_call(
        self,
        prompt: str,
        candidate_count: int,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> List[Tuple[str, Optional[float]]]:
        candidate_count = max(1, min(8, int(candidate_count)))  # Gemini cap

        gen_cfg: Dict[str, Any] = {
            "candidate_count": candidate_count,
            "response_logprobs": True,
        }
        if temperature is not None:
            gen_cfg["temperature"] = float(temperature)
        if top_p is not None:
            gen_cfg["top_p"] = float(top_p)
        if max_tokens is not None:
            gen_cfg["max_output_tokens"] = int(max_tokens)

        response = self.model.generate_content(prompt, generation_config=gen_cfg)
        cands = getattr(response, "candidates", None)
        if not cands:
            feedback = getattr(response, "prompt_feedback", "No feedback available.")
            print("Gemini API Warning: No candidates returned. Feedback:", feedback)
            return []

        outs: List[Tuple[str, Optional[float]]] = []
        for cand in cands:
            text = ""
            try:
                if hasattr(cand, 'content') and hasattr(cand.content, 'parts'):
                    text_parts = []
                    for part in cand.content.parts:
                        if hasattr(part, 'text'):
                            text_parts.append(part.text)
                    text = "".join(text_parts).strip()
            except Exception:
                continue
            if not text:
                continue
            score = self._average_logprob_from_candidate(cand)
            outs.append((text, score))
        return outs

    def generate_many_with_scores(
        self,
        prompt: str,
        n: int,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        per_request_cap: int = 8,
    ) -> List[Tuple[str, Optional[float]]]:
        outs: List[Tuple[str, Optional[float]]] = []
        remaining = int(n)
        while remaining > 0:
            take = min(remaining, per_request_cap)
            try:
                batch = self._single_call(
                    prompt=prompt,
                    candidate_count=take,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens,
                )
            except Exception as e:
                print(f"Gemini API Call Error: {e}")
                break
            if not batch:
                break
            outs.extend(batch)
            remaining -= len(batch)
        return outs[:n]


class OpenAIProvider:
    """OpenAI Chat Completions wrapper (works for vLLM-compatible servers via base_url)."""

    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: Optional[str] = None):
        if not api_key:
            raise RuntimeError("OpenAI-compatible API key is required (can be 'EMPTY' for vLLM).")
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)
        self.model = model

    @staticmethod
    def _average_logprob(choice) -> Optional[float]:
        try:
            lp = getattr(choice, "logprobs", None)
            if not lp or not getattr(lp, "content", None):
                return None
            token_logprobs: List[float] = []
            for item in lp.content:
                if item is None:
                    continue
                val = getattr(item, "logprob", None)
                if val is None:
                    continue
                token_logprobs.append(float(val))
            if not token_logprobs:
                return None
            return float(sum(token_logprobs) / len(token_logprobs))
        except Exception:
            return None

    @backoff(tries=3, base=0.5, factor=2.0)
    def _call_once(self, payload: Dict[str, Any]):
        return self.client.chat.completions.create(**payload)

    def generate_many_with_scores(
        self,
        messages: List[dict],
        n: int,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        per_request_cap: int = 8,
    ) -> List[Tuple[str, Optional[float]]]:
        outs: List[Tuple[str, Optional[float]]] = []
        remaining = int(n)
        while remaining > 0:
            take = min(per_request_cap, remaining)
            payload: Dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "n": int(take),
                "logprobs": True,
                "top_logprobs": 1,
            }
            if temperature is not None:
                payload["temperature"] = float(temperature)
            if top_p is not None:
                payload["top_p"] = float(top_p)
            if max_tokens is not None:
                payload["max_tokens"] = int(max_tokens)

            try:
                resp = self._call_once(payload)
            except Exception as e:
                print(f"OpenAI API Call Error: {e}")
                break

            choices = getattr(resp, "choices", None)
            if not choices:
                print("OpenAI API Warning: No choices returned.")
                break

            for ch in choices:
                txt = getattr(getattr(ch, "message", None), "content", None)
                if not txt:
                    continue
                score = self._average_logprob(ch)
                outs.append((txt.strip(), score))
            remaining -= take

        return outs[:n]


class AzureOpenAIProvider:
    """Azure OpenAI Chat Completions wrapper (deployment name in `model`)."""

    def __init__(
        self,
        azure_endpoint: str,
        api_key: str,
        api_version: str = "2024-02-15-preview",
        deployment: str = "",
    ):
        if not azure_endpoint:
            raise RuntimeError("Azure endpoint is required, e.g. https://<resource>.openai.azure.com/")
        if not api_key:
            raise RuntimeError("Azure OpenAI API key is required.")
        if not deployment:
            raise RuntimeError("Azure deployment name is required (use --azure-deployment).")

        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint.rstrip("/"),
            api_version=api_version or "2024-02-15-preview",
        )
        self.deployment = deployment

    @staticmethod
    def _average_logprob(choice) -> Optional[float]:
        try:
            lp = getattr(choice, "logprobs", None)
            if not lp or not getattr(lp, "content", None):
                return None
            vals: List[float] = []
            for item in lp.content:
                if item and getattr(item, "logprob", None) is not None:
                    vals.append(float(item.logprob))
            return float(sum(vals) / len(vals)) if vals else None
        except Exception:
            return None

    @backoff(tries=3, base=0.5, factor=2.0)
    def _call_once(self, payload: Dict[str, Any]):
        return self.client.chat.completions.create(**payload)

    def generate_many_with_scores(
        self,
        messages: List[dict],
        n: int,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        per_request_cap: int = 8,
    ) -> List[Tuple[str, Optional[float]]]:
        outs: List[Tuple[str, Optional[float]]] = []
        remaining = int(n)
        while remaining > 0:
            take = min(per_request_cap, remaining)
            payload: Dict[str, Any] = {
                "model": self.deployment,
                "messages": messages,
                "n": int(take),
                "logprobs": True,
                "top_logprobs": 1,
            }
            if temperature is not None:
                payload["temperature"] = float(temperature)
            if top_p is not None:
                payload["top_p"] = float(top_p)
            if max_tokens is not None:
                payload["max_tokens"] = int(max_tokens)

            try:
                resp = self._call_once(payload)
            except Exception as e:
                print(f"Azure OpenAI API Call Error: {e}")
                break

            choices = getattr(resp, "choices", None)
            if not choices:
                print("Azure OpenAI Warning: No choices returned.")
                break

            for ch in choices:
                txt = getattr(getattr(ch, "message", None), "content", None)
                if not txt:
                    continue
                score = self._average_logprob(ch)
                outs.append((txt.strip(), score))
            remaining -= take

        return outs[:n]


# Unified dispatcher
def chat_completions_with_scores(
    provider_name: str,
    provider_obj: Union[GeminiProvider, OpenAIProvider, AzureOpenAIProvider],
    messages: List[dict],
    n: int,
    temperature: Optional[float],
    top_p: Optional[float],
    max_tokens: Optional[int],
) -> List[Tuple[str, Optional[float]]]:
    if provider_name == "gemini":
        # Flatten system+user messages to a single prompt
        sys_txt, user_txt = "", ""
        for m in messages:
            role = m.get("role")
            if role == "system":
                sys_txt += (m.get("content", "") or "") + "\n\n"
            elif role == "user":
                user_txt += (m.get("content", "") or "") + "\n"
        final_prompt = (sys_txt.strip() + "\n\n" + user_txt.strip()).strip()
        return provider_obj.generate_many_with_scores(
            prompt=final_prompt,
            n=n,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
    elif provider_name in ("openai", "vllm", "azure"):
        return provider_obj.generate_many_with_scores(
            messages=messages,
            n=n,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


# =======================
# Problem utilities
# =======================

SYSTEM_PROMPT = (
"ROLE\n"
"You are an expert in Euclidean plane geometry. Given a formal geometry problem, "
"you propose ONLY the next auxiliary constructions required for the solution.\n"
"\n"
"INPUT ASSUMPTIONS\n"
"- The problem provides a symbol table of existing objects: points (A,B,C,...), lines (line(A,B)), "
"  and circles (circle(O,A) meaning center O, radius OA). Only use existing objects and any new "
"  points you create in THIS output line.\n"
"\n"
"OUTPUT FORMAT (STRICT)\n"
"- Output EXACTLY ONE line (one logical line; no explanations, no comments, no extra lines).\n"
"- The line is a comma-and-space separated list of construction clauses.\n"
"- Each clause has the form: v = construct_fn(arg1, arg2, ...)\n"
"- Use lowercase single letters (a,b,c,...) for NEW points; never reuse names already in the symbol table.\n"
"- You MAY add up to TWO clauses for the SAME new point to impose two independent constraints "
"  (repeat the same left-hand variable). Do not exceed two constraints per new point.\n"
"- Whitespace is normalized as: single space around '=' and after commas; no trailing period.\n"
"- Grammar (EBNF): line := clause {', ' clause}; clause := var ' = ' fn '(' args ')'; "
"  var := [a-z]; fn := 'construct_' identifier; args := obj {', ' obj}; "
"  obj := var | [A-Z] | 'line(' [A-Z] ',' [A-Z] ')' | 'circle(' [A-Z] ',' [A-Z] ')'.\n"
"\n"
"DETERMINISM & TIE-BREAKING\n"
"- Functions that could return two intersections take an anchor argument to disambiguate; "
"  when an anchor is present, return the intersection DISTINCT from the anchor point.\n"
"- Constructions assume general position (no degenerate/undefined cases unless implied by inputs).\n"
"\n"
"CONSTRUCTION LIBRARY (SIGNATURE → SEMANTICS)\n"
"- construct_free() → Point\n"
"- construct_segment() → (Point, Point)\n"
"- construct_triangle() → (Point, Point, Point)\n"
"- construct_angle_bisector(A,B,C) → Point X\n"
"- construct_circumcenter(A,B,C) → Point X\n"
"- construct_incenter(A,B,C) → Point X\n"
"- construct_orthocenter(A,B,C) → Point X\n"
"- construct_midpoint(A,B) → Point X\n"
"- construct_mirror(A,B) → Point X\n"
"- construct_reflect(A,B,C) → Point X\n"
"- construct_on_line(A,B) → Point X\n"
"- construct_on_pline(A,B,C) → Point X with XA ∥ BC\n"
"- construct_on_tline(A,B,C) → Point X with XA ⟂ BC\n"
"- construct_on_bline(A,B) → Point X\n"
"- construct_on_circle(O,A) → Point X\n"
"- construct_on_dia(A,B) → Point X with ∠AXB = 90°\n"
"- construct_eqdistance(A,B,C) → Point X with |XA| = |BC|\n"
"- construct_eqangle2(A,B,C) → Point X with ∠BAX = ∠XCB\n"
"- construct_eqangle3(A,B,D,E,F) → Point X with ∠XAB = ∠DEF\n"
"- construct_foot(A,B,C) → Point X (foot from A to BC)\n"
"- construct_lc_tangent(A,O) → Point X (AX ⟂ OA)\n"
"- construct_intersection_ll(A,B,C,D) → Point X\n"
"- construct_intersection_lc(A,O,B) → Point X (other than A)\n"
"- construct_intersection_cc(O,W,A) → Point X (other than A)\n"
"- construct_intersection_lp(A,B,C,M,N) → Point X\n"
"- construct_intersection_lt(A,B,C,D,E) → Point X\n"
"- construct_intersection_pp(A,B,C,D,E,F) → Point X\n"
"- construct_intersection_tt(A,B,C,D,E,F) → Point X\n"
"\n"
"QUALITY & SCOPE\n"
"- Prefer standard, minimal steps common in Olympiad geometry.\n"
"- Output only constructions; no prose.\n"
"\n"
"EXAMPLES\n"
"   h = construct_on_line(e,f), h = construct_on_circle(o,a)\n"
"   p = construct_midpoint(a,b), q = construct_on_tline(q0,c,d)\n"
"   x = construct_intersection_lc(a,o,b), y = construct_intersection_cc(o,w,a)\n"
)

SYSTEM_PROMPT2 = (
    "You are an expert in plane geometry, specializing in identifying the most effective "
    "auxiliary constructions for solving geometry problems. Given a formal geometry problem, "
    "output only the essential auxiliary constructions required for the solution. "
    "Use existing points as inputs and give unique names to all newly constructed points. "
    "Each new point must be defined using no more than two auxiliary constructions."
)


MAX_DIAGRAM_ATTEMPTS = None  # pass-through to your utils if needed


def build_problem_json(constructions_list, state: State) -> Dict[str, str]:
    constructions = [c for group in constructions_list for c in group]
    problem_str = ", ".join(str(c) for c in constructions)
    goal_str = str(state.goal)
    return {"problem": problem_str, "goal": goal_str}


def solve_with_engine(state: State, timeout_s: int) -> Tuple[bool, float]:
    dd = DeductiveDatabase(state)
    alg = AlgebraicSystem(state)
    eng = Engine(state, dd, alg)
    t0 = time.time()
    try:
        with TT(timeout_s):
            eng.run()
    except Exception as e:
        print(f"[engine] Exception during run: {e}")
    return (state.complete() is not None, time.time() - t0)


def generate_proof_str(state: State, timeout_s: int) -> Optional[str]:
    pg = ProofGenerator(state)
    pg.max_equation_length_perstep = None
    try:
        with TT(timeout_s):
            pg.run()
            proof = pg.get_proof()
            if proof is None:
                return None
            return pg.get_proof_str()
    except Exception as e:
        print(f"[proof] Exception during proof generation: {e}")
        return None


def group_aux_by_outputs(aux) -> List[List[Any]]:
    grouped: List[List[Any]] = []
    for construction in aux:
        if not grouped:
            grouped.append([construction])
        else:
            last = grouped[-1]
            if len(last[-1].outputs) == len(construction.outputs) and all(
                o1 == o2 for o1, o2 in zip(last[-1].outputs, construction.outputs)
            ):
                last.append(construction)
            else:
                grouped.append([construction])
    return grouped


def evaluate_with_aux_sequence(
    aux_sequence_text: str,
    base_state: State,
    constructions_list,
    engine_timeout_s: int,
    proof_timeout_s: int,
) -> Optional[Tuple[str, List]]:
    """Apply parsed aux constructions (single comma-separated line) and try to solve."""
    try:
        aux = parse_construction_program(aux_sequence_text)
    except Exception:
        return None

    aux_grouped = group_aux_by_outputs(aux)

    st = State()
    st.silent = True
    st.goal = base_state.goal
    st.diagram = copy.deepcopy(base_state.diagram)

    try:
        for group in aux_grouped:
            st.diagram.add_constructions(group)
    except Exception:
        return None

    try:
        for group in constructions_list + aux_grouped:
            st.add_constructions(group)
    except Exception:
        return None

    solved, _ = solve_with_engine(st, engine_timeout_s)
    if not solved:
        return None

    proof_str = generate_proof_str(st, proof_timeout_s)
    if not proof_str:
        return None
    return proof_str, aux


def format_proof_with_aux(aux, proof_str: str) -> str:
    aux_line = ", ".join(str(a) for a in aux)
    return f"Auxiliary constructions:\n{aux_line}\n{proof_str}"


# =======================
# Beam Search (single-line accumulation)
# =======================

def build_user_prompt(problem_str: str, goal_str: str, decided_text: str) -> str:
    """User message at each depth. Appends all decided constructions so far as ONE line."""
    if decided_text:
        problem_str = problem_str + ', ' + decided_text
    preface = f"Problem: {problem_str}\nGoal: {goal_str}\n"
    return preface


def run_beam_search_aux(
    provider_name: str,
    provider_obj: Union[GeminiProvider, OpenAIProvider, AzureOpenAIProvider],
    problem_str: str,
    goal_str: str,
    base_state: State,
    constructions_list,
    result_dir: Path,
    engine_timeout_s: int,
    proof_timeout_s: int,
    branching_factor: int,
    beam_size: int,
    max_depth: int,
    temperature: Optional[float],
    top_p: Optional[float],
    max_tokens: Optional[int],
    cpu_workers: int,
) -> Optional[Tuple[str, str]]:
    """
    Beam item = (cum_score, decided_text) where decided_text is ONE comma-separated line.
    At each depth:
      - Expand each beam item with 'branching_factor' samples (rank by logprob when available).
      - Keep top 'beam_size' by cumulative mean step score.
      - Early stop if any candidate solves the problem.
    Returns (proof_str, final_aux_text) if solved; otherwise None.
    """
    beam: List[Tuple[float, str]] = [(0.0, "")]  # start empty

    for depth in range(1, max_depth + 1):
        expansions: List[Tuple[float, str, str, Optional[float]]] = []

        for cum_score, decided_text in beam:
            user_content = build_user_prompt(problem_str, goal_str, decided_text)
            sys_prompt = SYSTEM_PROMPT2 if provider_name == "vllm" else SYSTEM_PROMPT
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_content},
            ]
            # print('messages', messages)
            samples = chat_completions_with_scores(
                provider_name=provider_name,
                provider_obj=provider_obj,
                messages=messages,
                n=max(1, branching_factor),
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )
            # print('outputs', samples)
            cleaned: List[Tuple[str, Optional[float]]] = []
            for txt, score in samples:
                cand = normalize_one_line(txt)
                if not cand:
                    continue
                cleaned.append((cand, score))

            seen_local: Set[str] = set()
            for cand, score in cleaned:
                if cand in seen_local:
                    continue
                seen_local.add(cand)
                step_score = normalize_score(score)
                new_score = cum_score + step_score
                expansions.append((new_score, decided_text, cand, step_score))

        if not expansions:
            return None

        expansions.sort(key=lambda x: x[0], reverse=True)
        top_expansions = expansions[:max(beam_size, 1)]

        eval_payloads: List[Tuple[float, str]] = []
        for new_score, decided_text, candidate_line, _step_score in top_expansions:
            new_text = candidate_line if not decided_text else f"{decided_text}, {candidate_line}"
            eval_payloads.append((new_score, new_text))

        def _eval_one(item: Tuple[float, str]):
            new_score, aux_text = item
            res = evaluate_with_aux_sequence(
                aux_sequence_text=aux_text,
                base_state=base_state,
                constructions_list=constructions_list,
                engine_timeout_s=engine_timeout_s,
                proof_timeout_s=proof_timeout_s,
            )
            return (new_score, aux_text, res)

        next_beam_candidates: List[Tuple[float, str]] = []
        with ThreadPoolExecutor(max_workers=max(1, cpu_workers)) as ex:
            futs = [ex.submit(_eval_one, item) for item in eval_payloads]
            for fut in as_completed(futs):
                try:
                    new_score, aux_text, res = fut.result()
                except Exception as e:
                    print(f"[beam-eval] worker error: {e}")
                    continue
                if res:
                    proof_str, _aux_objs = res
                    return proof_str, aux_text
                next_beam_candidates.append((new_score, aux_text))

        if not next_beam_candidates:
            return None

        agg: Dict[str, float] = {}
        for score, text in next_beam_candidates:
            if text not in agg or score > agg[text]:
                agg[text] = score
        beam = sorted([(s, t) for t, s in agg.items()], key=lambda x: x[0], reverse=True)[:max(beam_size, 1)]

    return None  # Exhausted max_depth


# =======================
# Hard-timeout process helpers
# =======================

def _model_tag_from_args(args) -> str:
    if args.provider == "gemini":
        return args.gemini_model
    if args.provider == "openai":
        return args.openai_model
    if args.provider == "vllm":
        return Path(args.vllm_model).name
    if args.provider == "azure":
        return args.azure_deployment
    raise ValueError(f"Unknown provider: {args.provider}")


def _make_provider(args):
    if args.provider == "gemini":
        return GeminiProvider(api_key=args.gemini_api_key, model=args.gemini_model)
    if args.provider == "openai":
        return OpenAIProvider(api_key=args.openai_api_key, model=args.openai_model)
    if args.provider == "vllm":
        base_url = args.vllm_base_url
        if not base_url.endswith("/v1"):
            base_url += "/v1"
        return OpenAIProvider(api_key=args.vllm_api_key or "EMPTY",
                              model=args.vllm_model, base_url=base_url)
    if args.provider == "azure":
        return AzureOpenAIProvider(azure_endpoint=args.azure_endpoint,
                                   api_key=args.azure_api_key,
                                   api_version=args.azure_api_version,
                                   deployment=args.azure_deployment)
    raise ValueError(f"Unknown provider: {args.provider}")


def _solve_one_problem_worker(problem_id: int, filtered_idx: int, orig_idx: int, text: str, args):
    """Executes one problem in a separate process. Killed by parent on timeout."""
    # Start a new session so parent can kill the whole process group.
    try:
        os.setsid()
    except Exception:
        pass

    model_tag = _model_tag_from_args(args)
    result_dir = args.results_dir / f"{problem_id}"
    ensure_dir(result_dir)
    proof_path = result_dir / "proof.txt"
    aux_proof_path = result_dir / f"{model_tag}_proof.txt"

    state = State()
    state.silent = True

    diagram_path = result_dir / "diagram.jpg"
    constructions_list = state.load_problem_from_text(str(text), str(diagram_path))

    data_json = result_dir / "data.json"
    if not data_json.exists():
        write_json_atomic(data_json, build_problem_json(constructions_list, state))

    data = json.loads(data_json.read_text(encoding="utf-8"))
    problem_str, goal_str = data["problem"], data["goal"]

    # Try pure engine first
    if not proof_path.exists():
        solved, elapsed = solve_with_engine(state, args.engine_timeout)
        if solved:
            print(f"[{problem_id}] Solved by engine in {elapsed:.2f}s; generating proof...")
            proof_str = generate_proof_str(state, args.proof_timeout)
            if proof_str:
                write_text_atomic(proof_path, proof_str)
                print(f"[{problem_id}] Proof generated and saved.")
                return

    print(
        f"[{problem_id}] Running beam search: branching={args.branching_factor}, "
        f"beam_size={args.beam_size}, max_depth={args.max_depth}"
    )

    provider = _make_provider(args)
    res = run_beam_search_aux(
        provider_name=args.provider,
        provider_obj=provider,
        problem_str=problem_str,
        goal_str=goal_str,
        base_state=state,
        constructions_list=constructions_list,
        result_dir=result_dir,
        engine_timeout_s=args.engine_timeout,
        proof_timeout_s=args.proof_timeout,
        branching_factor=args.branching_factor,
        beam_size=args.beam_size,
        max_depth=args.max_depth,
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        cpu_workers=args.cpu_workers,
    )

    if res is not None:
        proof_str, aux_text = res  # single merged line
        payload = "Auxiliary constructions:\n" + aux_text + "\n" + proof_str
        write_text_atomic(aux_proof_path, payload)
        print(f"[{problem_id}] Solved via beam search; proof saved.")
    else:
        print(f"[{problem_id}] Not solved after beam search (depth={args.max_depth}).")


def _run_problem_hard_timeout(problem_id: int, filtered_idx: int, orig_idx: int, text: str, args):
    """Run one problem in a child process; kill process group on timeout."""
    ctx = mp.get_context("fork")  # Slurm/Linux -> 'fork' is efficient
    p = ctx.Process(target=_solve_one_problem_worker,
                    args=(problem_id, filtered_idx, orig_idx, text, args),
                    daemon=False)
    p.start()
    p.join(args.problem_timeout)
    if p.is_alive():
        print(f"[{problem_id}] HARD TIMEOUT after {args.problem_timeout}s; killing process group...")
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)  # nuke the whole group
        except Exception:
            p.terminate()  # fallback
        p.join()


# =======================
# Main
# =======================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["gemini", "openai", "vllm", "azure"], required=True)

    # Gemini
    parser.add_argument("--gemini-model", type=str, default="gemini-2.5-pro")
    parser.add_argument("--gemini-api-key", type=str, default=os.environ.get("GEMINI_API_KEY", ""))

    # OpenAI (official)
    parser.add_argument("--openai-model", type=str, default="gpt-4o")
    parser.add_argument("--openai-api-key", type=str, default=os.environ.get("OPENAI_API_KEY", ""))

    # vLLM (OpenAI-compatible)
    parser.add_argument("--vllm-model", type=str, default="qwen2_5-math-7b")
    parser.add_argument("--vllm-base-url", type=str, default="http://localhost:8000/v1")
    parser.add_argument("--vllm-api-key", type=str, default=os.environ.get("VLLM_API_KEY", "EMPTY"))

    # Azure OpenAI
    parser.add_argument("--azure-endpoint", type=str, default=os.environ.get("AZURE_OPENAI_ENDPOINT", ""))
    parser.add_argument("--azure-api-key", type=str, default=os.environ.get("AZURE_OPENAI_API_KEY", ""))
    parser.add_argument("--azure-api-version", type=str, default=os.environ.get("AZURE_OPENAI_API_VERSION", ""))
    parser.add_argument("--azure-deployment", type=str, default=os.environ.get("AZURE_OPENAI_DEPLOYMENT", ""))

    # Data / results
    parser.add_argument("--data-txt", type=Path, default=Path("data/JGEX-AG-231.txt"))
    parser.add_argument("--results-dir", type=Path, default=Path("results/JGEX-AG-231"))

    # Beam search settings
    parser.add_argument("--branching-factor", type=int, default=32)
    parser.add_argument("--beam-size", type=int, default=128)
    parser.add_argument("--max-depth", type=int, default=4)

    # Common sampling / batching (only included if not None)
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument("--top-p", type=float, default=None)

    # CPU workers and timeouts
    parser.add_argument("--cpu-workers", type=int, default=32)
    parser.add_argument("--engine-timeout", type=int, default=1200)
    parser.add_argument("--proof-timeout", type=int, default=1200)

    # NEW: overall per-problem wall-clock cap (hard kill)
    parser.add_argument("--problem-timeout", type=int, default=5400,
                        help="Overall wall-clock seconds allowed per problem (default: 1.5h)")

    # Misc
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()
    random.seed(args.seed)

    # Optional: pass-through to your utils
    utils.MAX_DIAGRAM_ATTEMPTS = MAX_DIAGRAM_ATTEMPTS

    task_id, task_count = get_array_info()
    model_tag_for_naming = _model_tag_from_args(args)
    print(
        f"[Array shard] task {task_id}/{task_count} "
        f"provider={args.provider} model_tag={model_tag_for_naming} "
        f"branching={args.branching_factor} beam_size={args.beam_size} max_depth={args.max_depth} "
        f"cpu_workers={args.cpu_workers} problem_timeout={args.problem_timeout}s"
    )

    ensure_dir(args.results_dir)

    # Load problems
    data_txt = args.data_txt
    if not data_txt.exists():
        raise FileNotFoundError(f"--data-txt not found: {data_txt}")
    texts = parse_texts_from_file(Path(data_txt))

    # Filter candidates (skip already-solved)
    candidates: List[Tuple[int, str]] = []
    for idx, text in enumerate(texts):
        problem_id = idx + 1
        result_dir = args.results_dir / f"{problem_id}"
        ensure_dir(result_dir)
        proof_path = result_dir / "proof.txt"
        aux_proof_path = result_dir / f"{model_tag_for_naming}_proof.txt"
        if proof_path.exists() or aux_proof_path.exists():
            continue
        candidates.append((idx, text))

    if not candidates:
        print(f"[Array {task_id}] Nothing to do (all proofs present).")
        return

    tot = 0
    solved_cnt = 0

    for filtered_idx, (orig_idx, text) in enumerate(candidates):
        if not is_my_index(filtered_idx, task_id, task_count):
            continue

        problem_id = orig_idx + 1
        result_dir = args.results_dir / f"{problem_id}"
        ensure_dir(result_dir)

        print(f"[{problem_id}] Processing (filtered_idx {filtered_idx}, task {task_id})")
        tot += 1

        # Run in hard-timeout child process
        _run_problem_hard_timeout(problem_id, filtered_idx, orig_idx, text, args)

        # Check if solved after child exit (or kill)
        proof_path = result_dir / "proof.txt"
        aux_proof_path = result_dir / f"{model_tag_for_naming}_proof.txt"
        if proof_path.exists() or aux_proof_path.exists():
            solved_cnt += 1
        else:
            print(f"[{problem_id}] Unsolved/Timed out; no proof files found.")

    ratio = (solved_cnt / tot) if tot else 0.0
    print(f"[Array {task_id}] Solved {solved_cnt}/{tot} = {ratio:.2%}")


if __name__ == "__main__":
    main()
