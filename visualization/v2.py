#!/usr/bin/env python3
import json
import mimetypes
import os
import sys
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

HTML = r"""<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Geometry Problems Viewer</title>
<style>
  :root { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }
  body { margin: 24px; line-height: 1.5; }
  .wrap { max-width: 1000px; margin: 0 auto; }
  .controls { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
  .number { width: 100px; padding: 6px; font-size: 14px; }
  button { padding: 6px 10px; cursor: pointer; }
  .grid { display: grid; grid-template-columns: 1fr; gap: 16px; margin-top: 16px; }
  .panel { border: 1px solid #ddd; border-radius: 8px; padding: 12px; background: #fafafa; }
  .panel h3 { margin: 0 0 8px 0; font-size: 16px; }
  .imgbox { display: flex; flex-direction: column; gap: 8px; }
  .thumbs { display: flex; gap: 8px; flex-wrap: wrap; }
  .thumbs img { height: 60px; border: 1px solid #ccc; border-radius: 6px; cursor: pointer; }
  .mainimg { max-width: 100%; height: auto; border: 1px solid #ccc; border-radius: 8px; }
  textarea { width: 100%; min-height: 160px; padding: 8px; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
  .muted { color: #666; font-size: 12px; }
</style>
<div class="wrap">
  <h1>Geometry Problems Viewer</h1>
  <div class="controls">
    <label for="indexSel">Problem index:</label>
    <input id="indexSel" class="number" type="number" step="1" min="0" value="0">
    <span class="muted" id="countInfo"></span>
    <button id="prevBtn" title="Previous">◀ Prev</button>
    <button id="nextBtn" title="Next">Next ▶</button>
    <select id="jumpSel"></select>
  </div>

  <div class="grid">
    <div class="panel imgbox">
      <h3>Image</h3>
      <img id="mainImg" class="mainimg" alt="Problem image will appear here">
      <div id="thumbs" class="thumbs"></div>
      <div class="muted">
        Images are loaded from the absolute local paths in your JSON. We first try the path as-is;
        if your browser blocks <code>file://</code> images, we automatically fall back to a local proxy.
      </div>
    </div>

    <div class="panel">
      <h3>Instruction</h3>
      <textarea id="instruction" readonly></textarea>
    </div>

    <div class="panel">
      <h3>Solution</h3>
      <textarea id="solution" readonly></textarea>
    </div>
  </div>
</div>

<script>
  let DATA = [];
  let USE_PROXY = false; // set to true if file:// load fails once

  function toAsIsOrProxy(p) {
    if (!p) return "";
    if (USE_PROXY) {
      return "/proxy?path=" + encodeURIComponent(p);
    }
    // Use the path exactly as provided. If it looks absolute (starts with / or drive letter), prefix file://
    const looksAbsUnix = p.startsWith("/");
    const looksAbsWin = /^[A-Za-z]:[\\/]/.test(p);
    if (looksAbsUnix || looksAbsWin) {
      // Normalize Windows backslashes for file URLs
      const normalized = looksAbsWin ? "file:///" + p.replace(/\\/g, "/") : "file://" + p;
      return normalized;
    }
    return p; // relative as-is
  }

  async function loadData() {
    const res = await fetch("/data");
    if (!res.ok) throw new Error("Failed to fetch data");
    DATA = await res.json();
  }

  function el(id) { return document.getElementById(id); }
  const indexSel = el("indexSel");
  const countInfo = el("countInfo");
  const mainImg = el("mainImg");
  const thumbs = el("thumbs");
  const instruction = el("instruction");
  const solution = el("solution");
  const prevBtn = el("prevBtn");
  const nextBtn = el("nextBtn");
  const jumpSel = el("jumpSel");

  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

  function setImageWithFallback(urlPrimary, urlFallback) {
    return new Promise((resolve) => {
      mainImg.onload = () => resolve(true);
      mainImg.onerror = () => {
        if (!USE_PROXY && urlFallback) {
          USE_PROXY = true; // enable proxy permanently after first failure
          mainImg.src = urlFallback;
        }
        resolve(false);
      };
      mainImg.src = urlPrimary;
    });
  }

  async function show(idx) {
    if (idx < 0 || idx >= DATA.length) return;
    const item = DATA[idx] || {};
    instruction.value = item.instruction ?? "";
    solution.value = item.output ?? "";

    const imgs = Array.isArray(item.images) ? item.images : [];
    thumbs.innerHTML = "";

    if (imgs.length > 0) {
      const primary = toAsIsOrProxy(imgs[0]);
      const fallback = "/proxy?path=" + encodeURIComponent(imgs[0] || "");
      await setImageWithFallback(primary, fallback);
      mainImg.alt = `Image 0 for problem ${idx}`;
    } else {
      mainImg.removeAttribute("src");
      mainImg.alt = "No image";
    }

    imgs.forEach((p, i) => {
      const thumb = document.createElement("img");
      const asIs = toAsIsOrProxy(p);
      const prox = "/proxy?path=" + encodeURIComponent(p);
      thumb.src = USE_PROXY ? prox : asIs;
      thumb.alt = `Thumb ${i}`;
      thumb.title = p;
      thumb.addEventListener("click", () => {
        mainImg.src = USE_PROXY ? prox : asIs;
        mainImg.alt = `Image ${i} for problem ${idx}`;
      });
      thumbs.appendChild(thumb);
    });

    indexSel.value = String(idx);
    jumpSel.value = String(idx);
  }

  function wireControls() {
    const N = DATA.length;
    countInfo.textContent = `of ${Math.max(0, N - 1)} (0-based)`;
    indexSel.max = Math.max(0, N - 1);

    // Populate dropdown
    jumpSel.innerHTML = "";
    for (let i = 0; i < N; i++) {
      const item = DATA[i];
      const opt = document.createElement("option");
      opt.value = String(i);
      opt.textContent = `Index ${i}` + (item.index !== undefined && item.index !== i ? ` (label: ${item.index})` : "");
      jumpSel.appendChild(opt);
    }

    indexSel.addEventListener("change", () => {
      const idx = clamp(parseInt(indexSel.value || "0", 10), 0, N - 1);
      show(idx);
    });
    jumpSel.addEventListener("change", () => show(parseInt(jumpSel.value, 10)));
    prevBtn.addEventListener("click", () => {
      const cur = clamp(parseInt(indexSel.value || "0", 10), 0, N - 1);
      show(clamp(cur - 1, 0, N - 1));
    });
    nextBtn.addEventListener("click", () => {
      const cur = clamp(parseInt(indexSel.value || "0", 10), 0, N - 1);
      show(clamp(cur + 1, 0, N - 1));
    });
  }

  (async () => {
    await loadData();
    wireControls();
    show(0);
  })();
</script>
"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            self._send_html(HTML)
        elif parsed.path == "/data":
            self._send_json(self.server.dataset)
        elif parsed.path == "/proxy":
            qs = urllib.parse.parse_qs(parsed.query)
            path = qs.get("path", [""])[0]
            self._send_file(path)
        else:
            self.send_error(404, "Not Found")

    # Utilities
    def _send_html(self, html: str):
        data = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, obj):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, abs_path: str):
        # Security: allow only absolute paths on local filesystem
        if not abs_path:
            self.send_error(400, "Missing 'path' query parameter")
            return
        # Do not URL-decode twice; it's already decoded via parse_qs
        if not (abs_path.startswith("/") or (len(abs_path) > 2 and abs_path[1] == ":" and abs_path[2] in "\\/")):
            self.send_error(400, "Path must be absolute")
            return
        if not os.path.exists(abs_path):
            self.send_error(404, f"File not found: {abs_path}")
            return
        ctype, _ = mimetypes.guess_type(abs_path)
        ctype = ctype or "application/octet-stream"
        try:
            with open(abs_path, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

def run(json_path: str, port: int):
    # Load dataset once into memory (list of objects with fields: index, instruction, output, images)
    with open(json_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    # Normalize: ensure 'images' field is a list
    images_root = os.environ.get("IMAGES_ROOT", os.path.join(os.path.dirname(json_path), "images"))
    for item in dataset:
        imgs = item.get("images")
        imgs[0] = os.path.join(images_root, imgs[0].split("/")[-1])
        if imgs is None:
            item["images"] = []
        elif isinstance(imgs, str):
            item["images"] = [imgs]

    server = HTTPServer(("127.0.0.1", port), Handler)
    # Attach dataset to server instance
    server.dataset = dataset  # type: ignore[attr-defined]

    url = f"http://127.0.0.1:{port}/"
    print(f"Serving viewer on {url}")
    print("Tip: If images don't appear (browser blocks file://), they'll auto-switch to the /proxy loader on first failure.")

    # Open browser in a separate thread so server keeps running
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server.server_close()

if __name__ == "__main__":
    json_path = "data/task2/eval/data.json"
    port = 8000

    # Simple args: viewer.py [json_path] [--port N]
    args = sys.argv[1:]
    if args:
        # first positional (not starting with --) is path
        if not args[0].startswith("--"):
            json_path = args[0]
            args = args[1:]
        # parse --port
        for i, a in enumerate(args):
            if a == "--port" and i + 1 < len(args):
                try:
                    port = int(args[i + 1])
                except ValueError:
                    pass

    run(json_path, port)
