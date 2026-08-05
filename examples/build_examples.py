#!/usr/bin/env python3
"""Generate example predračun PDFs by seeding sample data into index.html
and printing through headless Chrome (A4)."""
import os, subprocess, pathlib, json

HERE = pathlib.Path("/Users/isakzvegelj/celesnik-predracun")
SRC = (HERE / "index.html").read_text(encoding="utf-8")
OUT = HERE / "examples"
OUT.mkdir(exist_ok=True)

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def build_demo(lang, sur, name, rows, fname):
    calls = "\n".join(
        f"      add({json.dumps(name_)},{price},{qty});"
        for name_, price, qty in rows
    )
    inject = f"""
<script>
(function(){{
  var btn = document.querySelector('#langGroup .btn[data-lang="{lang}"]');
  if(btn) btn.click();
  document.getElementById('surname').value={json.dumps(sur)};
  document.getElementById('pname').value={json.dumps(name)};
  document.getElementById('date').value='2026-08-05';
  function add(n,p,q){{ addRow(n,p); var r=document.querySelector('#items tr:last-child'); r.querySelector('.qty-i').value=q; }}
{calls}
  calc();
}})();
</script>
"""
    html = SRC.replace("</body>", inject + "</body>")
    p = OUT / fname
    p.write_text(html, encoding="utf-8")
    pdf = OUT / (fname.replace(".html", ".pdf"))
    cmd = [
        CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf}",
        f"--print-to-pdf-no-header",
        f"file://{p}",
    ]
    subprocess.run(cmd, capture_output=True)
    return pdf

# --- Example 1: Slovenian, prosthetic treatment ---
p1 = build_demo("sl", "Novak", "Ana", [
    ("Cirkonij prevleka", 470, 1),
    ("Porcelanska prevleka", 460, 1),
    ("Brušenje zoba", 120, 2),
    ("Provizorična prevleka", 45, 2),
    ("Anestezija", 20, 1),
], "predracun_priklad_sl.html")

# --- Example 2: Italian, implants ---
p2 = build_demo("it", "Rossi", "Marco", [
    ("Impianto", 800, 2),
    ("Abutment", 250, 2),
    ("Impronte", 120, 1),
    ("Chiave per impianti", 150, 1),
    ("Anestesia", 20, 1),
], "preventivo_esempio_it.html")

print("PDF1:", p1, os.path.getsize(p1))
print("PDF2:", p2, os.path.getsize(p2))
