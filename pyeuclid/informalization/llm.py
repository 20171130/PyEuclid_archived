import base64
from pathlib import Path
from typing import Optional, Union

# OpenAI / Azure OpenAI
from openai import OpenAI, AzureOpenAI
from openai.types.chat import ChatCompletionContentPartParam, ChatCompletionMessageParam

# Google Gemini
import google.generativeai as genai


# ---------- Helpers ----------
def path_to_b64_with_mime(path: Union[str, Path]) -> tuple[str, str]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Image not found: {p}")

    suffix = p.suffix.lower()
    if suffix in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    else:
        assert suffix == ".png"
        mime = "image/png"

    b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    return mime, b64


# ---------- OpenAI / AzureOpenAI Provider ----------
class OpenAIProvider:
    def __init__(self, client: Union[OpenAI, AzureOpenAI], model: str = "gpt-4o"):
        self.client = client
        self.model = model

    def _build_messages(
        self,
        user_prompt: str,
        image_path: Optional[Union[str, Path]],
    ) -> list[ChatCompletionMessageParam]:
        parts: list[ChatCompletionContentPartParam] = []
        if image_path:
            mime, b64 = path_to_b64_with_mime(image_path)
            parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"},
            })
        parts.append({"type": "text", "text": user_prompt})
        return [{"role": "user", "content": parts}]

    def generate(
        self,
        user_prompt: str,
        image_path: Optional[Union[str, Path]] = None,
        **kwargs,   # pass any sampling args here
    ) -> str:
        messages = self._build_messages(user_prompt, image_path)
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs,  # forwarded directly
        )
        return (resp.choices[0].message.content or "").strip()


# ---------- Gemini Provider ----------
class GeminiProvider:
    def __init__(self, api_key: str, model: str = "gemini-2.5-pro"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name=model)

    def _build_parts(
        self,
        user_prompt: str,
        image_path: Optional[Union[str, Path]],
    ):
        parts = []
        if image_path:
            mime, b64 = path_to_b64_with_mime(image_path)
            parts.append({"mime_type": mime, "data": b64})
        parts.append(user_prompt)
        return parts

    def generate(
        self,
        user_prompt: str,
        image_path: Optional[Union[str, Path]] = None,
        **kwargs,   # pass any Gemini generation args here
    ) -> str:
        parts = self._build_parts(user_prompt, image_path)

        # Gemini wants generation_config; map kwargs into it
        if kwargs:
            resp = self.model.generate_content(parts, generation_config=kwargs)
        else:
            resp = self.model.generate_content(parts)

        return (getattr(resp, "text", "") or "").strip()
