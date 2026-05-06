#!/usr/bin/env python3
# simple_geom_server.py
import json
import os
import re
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

JSON_PATH = os.environ.get("JSON_PATH", "./data/task2/eval/data.json")
IMAGES_ROOT = os.environ.get("IMAGES_ROOT", os.path.join(os.path.dirname(JSON_PATH), "images"))

def load_and_normalize(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    ours = {}
    with open("./results/task2/ours2.json", "r") as f:
        results = f.readlines()
        for result in results:
            if result[-1] == "\n": result = result[:-1]
            ours[json.loads(result)["index"]] = json.loads(result)["response_text"]

    # Normalize to a list of problems with: index, instruction, output, images[]
    problems = []
    if isinstance(data, dict):
        items = []
        for k, v in data.items():
            v = dict(v)
            v["index"] = int(k) if str(k).isdigit() else k
            items.append(v)
        data = items

    for i, p in enumerate(data):
        p = dict(p)
        # Ensure index exists
        p["index"] = p.get("index", i)
        # Clean "<image>" tag at the start of instruction if present
        instr = p.get("instruction", "")
        p["instruction"] = re.sub(r"^\s*<image>\s*\n?", "", instr, flags=re.IGNORECASE)
        # Normalize images to list[str]
        imgs = p.get("images") or []
        imgs[0] = os.path.join(IMAGES_ROOT, imgs[0].split("/")[-1])
        if isinstance(imgs, str):
            imgs = [imgs]
        p["images"] = imgs
        p["ours"] = ours[p["index"]]
        problems.append(p)
    return problems

PROBLEMS = load_and_normalize(JSON_PATH)
# Map index -> problem
INDEX = {str(p["index"]): p for p in PROBLEMS}

HTML_PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Geometry Problems Browser (no Flask)</title>
<style>
  :root {
    --bg:#0f172a; --panel:#111827; --muted:#94a3b8; --text:#e5e7eb;
    --accent:#22d3ee; --card:#1f2937; --border:#374151;
    --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    --sans: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans",
            "Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji";
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--text);font-family:var(--sans);line-height:1.5}
  header{padding:16px 20px;background:var(--panel);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:10}
  h1{margin:0;font-size:18px;letter-spacing:.3px}
  .container{max-width:1100px;margin:24px auto;padding:0 16px}
  .controls{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:16px}
  select,button,input[type="number"]{background:var(--card);color:var(--text);border:1px solid var(--border);padding:10px 12px;border-radius:10px;font-size:14px}
  button{cursor:pointer;transition:transform .05s ease;border-color:#475569}
  button:hover{transform:translateY(-1px)}
  .grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
  .card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:16px;box-shadow:0 10px 18px rgba(0,0,0,.18)}
  .card h2{margin:0 0 8px 0;font-size:16px;color:var(--accent)}
  .mono{font-family:var(--mono);white-space:pre-wrap}
  .image-wrap{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
  .image-wrap img{width:100%;height:auto;border-radius:10px;border:1px solid var(--border);background:#000}
  .muted{color:var(--muted);font-size:13px}
  .row{display:flex;gap:8px;align-items:center}
  .spacer{flex:1}
  .path{font-size:12px;color:var(--muted);word-break:break-all}
  footer{margin:28px 0 12px;text-align:center;color:var(--muted);font-size:12px}
  @media (max-width: 840px){ .grid{grid-template-columns:1fr} }
</style>
</head>
<body>
<header><h1>Geometry Problems Browser</h1></header>
<div class="container">
  <div class="controls">
    <label for="index">Problem index:</label>
    <select id="index"></select>
    <input id="goIdx" type="number" step="1" placeholder="Jump to index…"/>
    <button id="goBtn">Go</button>
    <div class="spacer"></div>
    <span class="muted" id="count"></span>
  </div>

  <div class="grid">
    <div class="card" id="problemCard">
      <h2>Problem</h2>
      <div class="row muted" id="meta"></div>
      <div class="image-wrap" id="images"></div>
      <div class="mono" id="instruction" style="margin-top:10px;"></div>
    </div>
    <div class="card" id="solutionCard">
      <h2>Solution</h2>
      <div class="mono" id="output"></div>
    </div>
    <div class="card" id="oursCard">
      <h2>Ours</h2>
      <div class="mono" id="ours"></div>
    </div>
  </div>

  <footer>
    Serving <span class="muted">/data</span> from the server; original file: <span class="muted">%(json_path)s</span>.
  </footer>
</div>

<script>
const $index = document.getElementById('index');
const $goIdx = document.getElementById('goIdx');
const $goBtn = document.getElementById('goBtn');
const $count = document.getElementById('count');
const $meta = document.getElementById('meta');
const $images = document.getElementById('images');
const $instruction = document.getElementById('instruction');
const $output = document.getElementById('output');
const $ours = document.getElementById('ours');

let PROBLEMS = [];
let BYIDX = {};
function setHash(idx){ window.location.hash = '#'+encodeURIComponent(idx); }
function getHash(){ return decodeURIComponent((window.location.hash||'').replace(/^#/, '')); }

async function loadAll(){
  const res = await fetch('/data');
  PROBLEMS = await res.json();
  BYIDX = {};
  PROBLEMS.forEach(p => BYIDX[String(p.index)] = p);

  $index.innerHTML = '';
  PROBLEMS.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.index;
    opt.textContent = p.index;
    $index.appendChild(opt);
  });
  $count.textContent = PROBLEMS.length + ' problems';
}

function render(idx){
  const p = BYIDX[String(idx)];
  if(!p){
    $instruction.textContent = 'Problem not found.';
    $output.textContent = '';
    $images.innerHTML = '';
    $meta.textContent = '';
    return;
  }
  [...$index.options].forEach(o => o.selected = (String(o.value)===String(idx)));
  $instruction.textContent = p.instruction || '(no instruction)';
  $output.textContent = p.output || '(no solution)';
  $ours.textContent = p.ours || '(no solution)';
  $images.innerHTML = '';
  $meta.innerHTML = `<span class="muted">index:</span>&nbsp;<code>${p.index}</code>`;

  (p.images || []).forEach((_, i) => {
    const wrap = document.createElement('div');
    const img = document.createElement('img');
    img.loading = 'lazy';
    img.src = '/image?idx=' + encodeURIComponent(p.index) + '&img=' + i;
    img.alt = `Problem ${p.index} image ${i+1}`;
    img.onerror = () => {
      img.replaceWith(document.createElement('div'));
      const fallback = document.createElement('div');
      fallback.className = 'path';
      const raw = (p.raw_image_paths && p.raw_image_paths[i]) || '(unknown path)';
      fallback.textContent = 'Image unavailable: ' + raw;
      wrap.appendChild(fallback);
    };
    wrap.appendChild(img);
    $images.appendChild(wrap);
  });

  setHash(p.index);
}

window.addEventListener('hashchange', () => {
  const idx = getHash();
  if (idx) render(idx);
});

$index.addEventListener('change', e => render(e.target.value));
$goBtn.addEventListener('click', () => {
  const idx = $goIdx.value.trim();
  if (idx) render(idx);
});

(async function init(){
  await loadAll();
  const target = getHash() || ($index.options[0] && $index.options[0].value);
  if (target) render(target);
})();
</script>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, obj, code=200):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_html(self, html: str, code=200):
        data = html.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, path: Path):
        if not path.exists() or not path.is_file():
            self.send_error(404, "File not found")
            return
        # naive mime: just let browser sniff; explicitly set octet-stream fallback
        self.send_response(200)
        # minimal content type handling for common image types
        suffix = path.suffix.lower()
        ctype = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".svg": "image/svg+xml",
            ".bmp": "image/bmp"
        }.get(suffix, "application/octet-stream")
        self.send_header("Content-Type", ctype)
        fs = path.stat()
        self.send_header("Content-Length", str(fs.st_size))
        self.end_headers()
        with path.open("rb") as f:
            self.wfile.write(f.read())

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            page = HTML_PAGE
            return self._send_html(page)

        if path == "/data":
            # Include raw_image_paths for helpful error text on the client
            payload = []
            for p in PROBLEMS:
                payload.append({
                    "index": p["index"],
                    "instruction": p.get("instruction", ""),
                    "output": p.get("output", ""),
                    "images": list(range(len(p.get("images", [])))),  # count only
                    "raw_image_paths": p.get("images", []),
                    "ours": p.get("ours", ""),
                })
                print(payload)
            return self._send_json(payload)

        if path == "/image":
            qs = urllib.parse.parse_qs(parsed.query)
            idx = (qs.get("idx", [None])[0])
            img_i = qs.get("img", [None])[0]
            if idx is None or img_i is None:
                return self.send_error(400, "Missing idx or img")
            prob = INDEX.get(str(idx))
            if not prob:
                return self.send_error(404, "Problem not found")
            try:
                i = int(img_i)
            except ValueError:
                return self.send_error(400, "img must be int")
            images = prob.get("images", [])
            if i < 0 or i >= len(images):
                return self.send_error(404, "Image index out of range")
            img_path = Path(images[i])
            return self._send_file(img_path)

        # Fallback
        self.send_error(404, "Not found")

def run(host="127.0.0.1", port=8000):
    server = HTTPServer((host, port), Handler)
    print(f"Serving on http://{host}:{port}")
    print(f"Using JSON: {JSON_PATH}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server.server_close()

if __name__ == "__main__":
    # Allow optional port argument
    p = 7000
    if len(sys.argv) >= 2:
        try:
            p = int(sys.argv[1])
        except ValueError:
            pass
    run(port=p)
