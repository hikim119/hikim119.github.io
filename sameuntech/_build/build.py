"""삼은테크 홈페이지 빌드.

페이지 본문은 _build/content.html 에 있고, 이 스크립트가 공통 틀(머리말·메뉴·서브 배너·탭·푸터)을
씌워 sameuntech/*.html 을 만든다. 본문은 content.html, 메뉴·회사 정보·아이콘은 이 파일을 고친 뒤:

    python sameuntech/_build/build.py

_build 폴더는 밑줄로 시작해서 GitHub Pages(Jekyll)가 공개하지 않는다.
사진은 sameuntech/img/ 에 넣고 content.html 의 <div class="ph ..."> 자리를 <img> 로 바꾼다.
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent

CO = {
    "name": "삼은테크", "ceo": "김광현", "bizno": "221-23-60415",
    "addr": "경기도 광명시 하안로 60, 광명SK테크노파크 C동 902호",
    "tel": "02-2083-2070", "tel_link": "0220832070", "email": "sameuntech@naver.com",
}

# (그룹 이름, [(파일 이름, 페이지 제목), ...]) — 첫 페이지가 그룹 대표 링크
MENU = [
    ("회사소개", [("greeting", "CEO 인사말"), ("overview", "개요"), ("history", "연혁"),
                ("organization", "조직도"), ("location", "찾아오시는 길")]),
    ("제조시스템", [("flow", "제조흐름도/고객발주"), ("equipment", "제조설비현황")]),
    ("제조공정", [("smt", "제조공정(SMT)"), ("pba", "제조공정(PBA·조립)")]),
    ("제조품목", [("products", "제조품목")]),
    ("고객센터", [("quote", "견적의뢰"), ("notice", "공지사항")]),
]

# 선 아이콘 (64x64). class="ac" 는 파란 강조.
_IC = {
    "pcb": '<rect x="8" y="12" width="48" height="40" rx="3"/><circle cx="16" cy="20" r="2.5"/><circle cx="48" cy="44" r="2.5"/><path d="M18 42h10l6-6h12M18 32h8"/><rect class="ac" x="32" y="18" width="14" height="10" rx="1"/>',
    "chip": '<rect x="18" y="18" width="28" height="28" rx="3"/><rect class="ac" x="25" y="25" width="14" height="14" rx="2"/><path d="M25 18v-8M32 18v-8M39 18v-8M25 54v-8M32 54v-8M39 54v-8M18 25h-8M18 32h-8M18 39h-8M54 25h-8M54 32h-8M54 39h-8"/>',
    "iron": '<path d="M36 28 50 14a4.2 4.2 0 0 1 6 6L42 34"/><path d="M36 28l-5 5 6 6 5-5"/><path d="M31 33 15 49"/><path d="M6 58h24"/><circle class="ac" cx="13" cy="51" r="4"/>',
    "inspect": '<circle cx="27" cy="27" r="16"/><path d="M39 39l15 15"/><path class="acs" d="M20 27l5 5 9-10"/>',
    "truck": '<path d="M5 16h32v28H5z"/><path d="M37 24h13l9 11v9H37z"/><circle cx="15" cy="47" r="5" fill="#fff"/><circle cx="48" cy="47" r="5" fill="#fff"/><rect class="ac" x="11" y="22" width="12" height="8"/>',
    "doc": '<path d="M15 6h24l11 11v41H15z"/><path d="M39 6v11h11"/><path d="M22 28h20M22 36h20M22 44h12"/>',
    "box": '<path d="M32 6 56 18v28L32 58 8 46V18z"/><path d="M8 18l24 12 24-12M32 30v28"/><path class="acs" d="M20 12l24 12"/>',
    "building": '<path d="M14 56V12h36v44"/><path d="M8 56h48"/><path d="M22 20v28M30 20v28M38 20v28M46 20"/><rect class="ac" x="28" y="44" width="8" height="12"/>',
    "growth": '<rect x="8" y="40" width="10" height="16"/><rect x="24" y="30" width="10" height="26"/><rect class="ac" x="40" y="20" width="10" height="36"/><path d="M8 28c12-8 22-12 38-20"/><path d="M39 7h8v8"/>',
}


def icon(name):
    return ('<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.6" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            + _IC[name].replace('class="ac"', 'fill="#3b7be6" stroke="none"')
                       .replace('class="acs"', 'stroke="#3b7be6"')
            + "</svg>")


SVG_HOME = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><path d="M3 11 12 3l9 8M5.5 9v11.5h13V9"/><path d="M10 20.5v-6h4v6"/></svg>'
SVG_MAIL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><rect x="2.5" y="5" width="19" height="14"/><path d="m2.5 5 9.5 8 9.5-8M2.5 19l7-6.5M21.5 19l-7-6.5"/></svg>'
SVG_MENU = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg>'


def head(title, desc):
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<!-- 시안 단계: 검색 노출 막음. 확정되면 build.py 에서 이 줄을 지운다 -->
<meta name="robots" content="noindex">
<meta property="og:type" content="website">
<meta property="og:title" content="삼은테크 | SMT · 수삽 · PCB 조립">
<meta property="og:description" content="샘플부터 소량다품종, 양산까지. 2007년부터 경기도 광명에서.">
<meta property="og:image" content="https://hikim119.github.io/sameuntech/og.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap">
<link rel="stylesheet" href="style.css">
</head>
<body>
"""


def header(group):
    items = []
    for g, pages in MENU:
        sub = "".join(f'<a href="{k}.html">{t}</a>' for k, t in pages) if len(pages) > 1 else ""
        on = ' class="on"' if g == group else ""
        items.append(f'<li{on}><a href="{pages[0][0]}.html">{g}</a>'
                     + (f'<div class="sub">{sub}</div>' if sub else "") + "</li>")
    smap = ""
    for g, pages in MENU:
        links = "".join('<a href="%s.html">%s</a>' % (k, t) for k, t in pages)
        smap += (f'<dl><dt><a href="{pages[0][0]}.html">{g}</a></dt>'
                 + (f"<dd>{links}</dd>" if len(pages) > 1 else "") + "</dl>")
    return f"""<header class="header">
  <div class="wrap">
    <a class="logo" href="index.html"><strong>삼은테크</strong><small>SAMEUN TECH</small></a>
    <ul class="gnb">{"".join(items)}</ul>
    <div class="util">
      <a class="home" href="index.html" aria-label="처음으로">{SVG_HOME}</a>
      <a href="quote.html" aria-label="견적의뢰">{SVG_MAIL}</a>
      <button type="button" id="menuOpen" aria-label="전체 메뉴" aria-expanded="false" aria-controls="sitemap">{SVG_MENU}</button>
    </div>
  </div>
</header>
<div class="sitemap" id="sitemap"><div class="sitemap-inner">
  <button type="button" class="sitemap-close" id="menuClose" aria-label="메뉴 닫기">&times;</button>
  <dl><dt><a href="index.html">처음으로</a></dt></dl>{smap}
</div></div>
"""


def sub_frame(group, key):
    pages = dict(MENU)[group]
    tabs = "".join('<li%s><a href="%s.html">%s</a></li>' % (' class="on"' if k == key else "", k, t)
                   for k, t in pages)
    return f"""<div class="svisual"><h2>{group}</h2></div>
<nav class="lnb" aria-label="{group} 메뉴"><ul>{tabs}</ul></nav>
"""


def footer():
    c = CO
    return f"""<footer class="footer">
  <div class="wrap">
    <a class="logo" href="index.html"><strong>삼은테크</strong><small>SAMEUN TECH</small></a>
    <div class="f-info">
      <p><span>상호 : {c["name"]}</span><span>대표자 : {c["ceo"]}</span><span>사업자등록번호 : {c["bizno"]}</span><span>E-mail : {c["email"]}</span></p>
      <p><span>주소 : {c["addr"]}</span><span>전화 : {c["tel"]}</span></p>
      <p class="f-copy">Copyright &copy; 삼은테크 All Rights Reserved</p>
    </div>
  </div>
</footer>
<script src="site.js"></script>
</body>
</html>
"""


def fill(body):
    body = re.sub(r"\{\{ICON_(\w+)\}\}", lambda m: icon(m.group(1)), body)
    for k, v in CO.items():
        body = body.replace("{{" + k + "}}", v)
    if "{{" in body:
        raise SystemExit("unfilled placeholder: " + body[body.index("{{"):][:40])
    return body


def main():
    text = (HERE / "content.html").read_text(encoding="utf-8")
    parts = re.split(r"^<!-- @page (\w+) -->[ \t]*$", text, flags=re.M)
    bodies = {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}
    group_of = {k: (g, t) for g, pages in MENU for k, t in pages}
    missing = (set(group_of) | {"index"}) - set(bodies)
    if missing:
        raise SystemExit(f"content.html 에 없는 페이지: {sorted(missing)}")

    desc = "삼은테크는 2007년부터 경기도 광명에서 SMT 실장, 수삽, PCB 조립을 해 온 전자부품 제조 기업입니다."
    out = {"index": head("삼은테크 | SMT · 수삽 · PCB 조립", desc) + header(None)
           + "<main>\n" + fill(bodies["index"]) + "\n</main>\n" + footer()}
    for key, (group, title) in group_of.items():
        out[key] = (head(f"{title} | 삼은테크", desc) + header(group) + sub_frame(group, key)
                    + f'<main class="content"><div class="wrap">\n{fill(bodies[key])}\n</div></main>\n' + footer())
    for key, html in out.items():
        (OUT / f"{key}.html").write_text(html, encoding="utf-8", newline="\n")
    print("built", len(out), "pages:", ", ".join(out))


if __name__ == "__main__":
    main()
