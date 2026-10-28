"""Build index.html from template.html and data/figures.json. No number is typed here: DATA is the extracted
figures file, whose MANIFEST names the summary file and sha behind each series. Refuses if figures.json's sha differs
from the one MANIFEST records.
    python build.py            -> index.html (full document, for GitHub Pages)
    python build.py --artifact PATH -> body-only copy for a claude.ai artifact preview
"""
import hashlib, json, os, sys
H = os.path.dirname(os.path.abspath(__file__))
fig = open(os.path.join(H, "data", "figures.json"), "rb").read()
man = open(os.path.join(H, "data", "MANIFEST"), encoding="utf-8").read()
want = [l.split()[-1] for l in man.splitlines() if l.startswith("figures.json")][0]
got = hashlib.sha256(fig).hexdigest()[:12]
if got != want:
    sys.exit(f"REFUSE: data/figures.json sha {got} != MANIFEST {want}")
data = json.loads(fig)
files = data["files"]["ll"]
w_files = {"ownrun": "ownrun " + files["ownrun/summary.json"], "llama": "ownrun_llama " + files["ownrun_llama/summary_home.json"],
           "smollm3": "ownrun_smollm3 " + files["ownrun_smollm3/summary.json"]}
tpl = open(os.path.join(H, "template.html"), encoding="utf-8").read()
body = tpl.replace("/*__DATA__*/", "const DATA = " + json.dumps(data) + "; const W_FILES = " + json.dumps(w_files) + ";")

if len(sys.argv) > 2 and sys.argv[1] == "--artifact":
    art = body.replace("<!--HEAD-->\n", "").replace("<!--/HEAD-->\n", "").replace(
        "<!--ARTIFACT-META-->", '<meta name="claude:viewport-fit-sides" content="cover">')
    open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(art)
    print("artifact copy", len(art), "bytes ->", sys.argv[2])
else:
    head = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="description" content="What a stale KV cache does to the model that reads it, across agent handoffs and policy updates.">\n')
    page = body.replace("<!--HEAD-->\n", head).replace("<!--ARTIFACT-META-->\n", "").replace("<!--/HEAD-->\n", "</head>\n<body>\n") + "</body>\n</html>\n"
    out = os.path.join(H, "index.html")
    open(out, "w", encoding="utf-8", newline="\n").write(page)
    print("index.html", len(page), "bytes; figures.json", got)
