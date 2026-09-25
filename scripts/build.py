"""skills/ 以下の SKILL.md から GitHub Pages 用のサイトと zip を作る。

使い方: python scripts/build.py   → _site/ に出力
"""

import html
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
OUT = ROOT / "_site"


def parse_frontmatter(text):
    """先頭の --- で囲まれた key: value を読む（1行の値のみ対応）。"""
    meta, body = {}, text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].strip().splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    meta[key.strip()] = value.strip().strip("\"'")
            body = text[end + 4:].lstrip("\n")
    return meta, body


def load_skills(categories):
    skills = []
    for skill_md in sorted(SKILLS_DIR.glob("*/*/SKILL.md")):
        folder = skill_md.parent
        category = folder.parent.name
        if category not in categories:
            raise SystemExit(f"categories.json に未登録のカテゴリです: {category}")
        meta, body = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        name = meta.get("name") or folder.name
        if name != folder.name:
            raise SystemExit(f"name とフォルダ名が一致しません: {name} / {folder.name}")
        title = next((l[2:].strip() for l in body.splitlines() if l.startswith("# ")), name)
        skills.append({
            "name": name,
            "title": title,
            "description": meta.get("description", ""),
            "category": category,
            "folder": folder,
            "markdown": skill_md.read_text(encoding="utf-8"),
        })
    return skills


def build_zip(skill):
    """claude.ai にそのままアップロードできる zip（<name>/SKILL.md ...）を作る。"""
    dest = OUT / "downloads" / f"{skill['name']}.zip"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(skill["folder"].rglob("*")):
            if f.is_file():
                zf.write(f, f"{skill['name']}/{f.relative_to(skill['folder']).as_posix()}")


STYLE = """
:root{--bg:#f7f6f3;--surface:#fff;--text:#1f1e1c;--muted:#6b6862;--line:#e4e1da;--accent:#b4532a;--accent-soft:#f6e7df}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#1b1a18;--surface:#252421;--text:#ecebe7;--muted:#a19d95;--line:#3a3833;--accent:#e8845a;--accent-soft:#3a2a22}}
:root[data-theme="dark"]{--bg:#1b1a18;--surface:#252421;--text:#ecebe7;--muted:#a19d95;--line:#3a3833;--accent:#e8845a;--accent-soft:#3a2a22}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.7 "Noto Sans JP",system-ui,sans-serif}
main{max-width:880px;margin:0 auto;padding:32px 16px 64px}
h1{font-size:1.6rem;margin:0 0 4px}
.lead{color:var(--muted);margin:0 0 24px}
input[type=search]{width:100%;padding:10px 14px;border:1px solid var(--line);border-radius:10px;background:var(--surface);color:var(--text);font:inherit;margin-bottom:28px}
section{margin-bottom:32px}
h2{font-size:1.1rem;margin:0}
.cat-desc{color:var(--muted);font-size:.9rem;margin:0 0 12px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin-bottom:12px}
.card h3{margin:0 0 4px;font-size:1rem}
.card p{margin:0 0 12px;color:var(--muted);font-size:.92rem}
.actions{display:flex;flex-wrap:wrap;gap:8px}
.btn{display:inline-block;padding:6px 14px;border-radius:8px;border:1px solid var(--line);color:var(--text);text-decoration:none;font-size:.9rem}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}
.empty{color:var(--muted);font-size:.9rem}
.back{color:var(--accent);text-decoration:none;font-size:.9rem}
.tag{display:inline-block;background:var(--accent-soft);color:var(--accent);border-radius:6px;padding:0 8px;font-size:.8rem;margin-bottom:8px}
article{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:8px 22px;margin-top:16px;overflow-wrap:anywhere}
article table{border-collapse:collapse;display:block;overflow-x:auto}
article pre{overflow-x:auto;background:var(--bg);padding:12px;border-radius:8px}
code{font-family:ui-monospace,monospace;font-size:.9em}
"""


def page(title, body):
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
<style>{STYLE}</style></head>
<body><main>{body}</main></body></html>
"""


def build_index(skills, categories):
    sections = []
    for key, cat in sorted(categories.items(), key=lambda kv: kv[1].get("order", 99)):
        items = [s for s in skills if s["category"] == key]
        cards = "".join(
            f"""<div class="card" data-search="{html.escape((s['name'] + s['title'] + s['description']).lower())}">
<h3>{html.escape(s['title'])}</h3><p>{html.escape(s['description'])}</p>
<div class="actions"><a class="btn primary" href="downloads/{s['name']}.zip">zipをダウンロード</a>
<a class="btn" href="skills/{s['name']}/">中身を見る</a></div></div>"""
            for s in items
        ) or '<p class="empty">まだありません</p>'
        sections.append(f"""<section><h2>{html.escape(cat['title'])}</h2>
<p class="cat-desc">{html.escape(cat.get('description', ''))}</p>{cards}</section>""")

    body = f"""<h1>Claude Skills</h1>
<p class="lead">日常を効率化するための自作スキル集（{len(skills)}件）。zipをclaude.aiの「設定 → 機能 → スキル」からアップロードして使います。</p>
<input type="search" id="q" placeholder="スキルを検索" aria-label="スキルを検索">
{''.join(sections)}
<script>
document.getElementById('q').addEventListener('input', e => {{
  const q = e.target.value.trim().toLowerCase();
  document.querySelectorAll('.card').forEach(c => c.hidden = q && !c.dataset.search.includes(q));
}});
</script>"""
    (OUT / "index.html").write_text(page("Claude Skills", body), encoding="utf-8")


def build_detail(skill, categories):
    dest = OUT / "skills" / skill["name"]
    dest.mkdir(parents=True, exist_ok=True)
    md_json = json.dumps(skill["markdown"], ensure_ascii=False).replace("</", "<\\/")
    body = f"""<a class="back" href="../../">← 一覧へ戻る</a>
<h1>{html.escape(skill['title'])}</h1>
<span class="tag">{html.escape(categories[skill['category']]['title'])}</span>
<p class="lead">{html.escape(skill['description'])}</p>
<div class="actions"><a class="btn primary" href="../../downloads/{skill['name']}.zip">zipをダウンロード</a></div>
<article id="md"><pre id="raw"></pre></article>
<script src="https://cdn.jsdelivr.net/npm/marked@12/marked.min.js"></script>
<script>
const src = {md_json};
const text = src.replace(/^---[\\s\\S]*?\\n---\\n/, '');
const el = document.getElementById('md');
if (window.marked) el.innerHTML = marked.parse(text);
else document.getElementById('raw').textContent = src;
</script>"""
    (dest / "index.html").write_text(page(skill["title"], body), encoding="utf-8")


def main():
    categories = json.loads((ROOT / "categories.json").read_text(encoding="utf-8"))
    skills = load_skills(categories)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for s in skills:
        build_zip(s)
        build_detail(s, categories)
    build_index(skills, categories)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"{len(skills)} 件のスキルを _site/ に出力しました")


if __name__ == "__main__":
    main()
