import os
import sys

pdf_url = os.environ["PDF_URL"]

with open("/tmp/body.html", "r", encoding="utf-8") as f:
    body = f.read()

css = """
@page { size: A4; margin: 12mm 15mm; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: "Noto Sans CJK JP", "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
  font-size: 10.5pt;
  line-height: 1.7;
  color: #1a1a1a;
  background: #f0f2f5;
}
.site-header {
  background: #1e293b;
  padding: 14px 24px;
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.site-header span { color: #94a3b8; font-size: 14px; }
.download-btn {
  display: inline-block;
  background: #e11d48;
  color: white;
  padding: 9px 22px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 14px;
  font-weight: bold;
  letter-spacing: 0.03em;
}
.download-btn:hover { background: #be123c; }
.content {
  max-width: 860px;
  margin: 40px auto;
  background: white;
  padding: 52px 60px;
  border-radius: 10px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.07);
}
h1 { font-size: 1.7em; color: #1e293b; margin-bottom: 6px; }
h2 {
  font-size: 1.2em;
  color: #1e293b;
  border-left: 4px solid #e11d48;
  padding-left: 12px;
  margin: 28px 0 10px;
}
h3 { font-size: 1.05em; color: #334155; margin: 16px 0 6px; }
p { margin: 6px 0; }
ul, ol { margin: 6px 0 6px 24px; }
li { margin: 2px 0; }
hr { border: none; border-top: 1px solid #e2e8f0; margin: 20px 0; }
table { border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 0.95em; }
th, td { border: 1px solid #e2e8f0; padding: 10px 14px; text-align: left; }
th { background: #f8fafc; font-weight: bold; color: #475569; }
tr:nth-child(even) td { background: #fafafa; }
code {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.88em;
}
strong { color: #1e293b; }
@media print {
  .site-header { display: none; }
  body { background: white; font-size: 10.5pt; }
  .content {
    box-shadow: none;
    border-radius: 0;
    margin: 0;
    padding: 0;
    max-width: 100%;
  }
  h2 { margin-top: 16pt; }
  a { color: inherit; text-decoration: none; }
}
@media (max-width: 768px) {
  .content { padding: 28px 20px; margin: 16px; }
}
"""

html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>職務経歴書</title>
  <style>{css}</style>
</head>
<body>
  <header class="site-header">
    <span>職務経歴書</span>
    <a href="{pdf_url}" class="download-btn" download>PDF ダウンロード</a>
  </header>
  <main class="content">
    {body}
  </main>
</body>
</html>"""

os.makedirs("dist", exist_ok=True)
with open("dist/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("HTML generated successfully")
