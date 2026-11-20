"""삼은테크 홈페이지 빌드.

페이지 본문은 _build/content.html 에 있고, 이 스크립트가 공통 틀(머리말·메뉴·서브 배너·탭·푸터)을
씌워 sameuntech/*.html 을 만든다. 본문은 content.html, 메뉴·회사 정보·아이콘은 이 파일을 고친 뒤:

    python sameuntech/_build/build.py

_build 폴더는 밑줄로 시작해서 GitHub Pages(Jekyll)가 공개하지 않는다.
사진은 sameuntech/img/ 에 넣고 content.html 의 <div class="ph ..."> 자리를 <img class="photo"> 로 바꾼다.
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent

CO = {
    "name": "삼은테크", "ceo": "김광현", "bizno": "221-23-60415",
    "addr": "경기도 광명시 하안로 60, 광명SK테크노파크 C동 902호",
    "tel": "02-2083-2070", "tel_link": "0220832070", "email": "sameuntech@naver.com",
    # 카카오톡 채널 1:1 채팅 주소 (예: http://pf.kakao.com/_xxxxxx/chat). 비어 있으면 "준비 중" 안내.
    "kakao": "",
}

# (그룹 이름, 배너 한 줄, [(파일 이름, 페이지 제목), ...]) — 첫 페이지가 그룹 대표 링크
MENU = [
    ("회사소개", "삼은테크는 2007년부터 경기도 광명에서 SMT · 수삽 · PCB 조립을 해 왔습니다.",
     [("greeting", "인사말"), ("history", "연혁"), ("location", "오시는길")]),
    ("사업내용", "샘플부터 소량다품종, 양산까지 정확한 납기와 품질로 보답하겠습니다.",
     [("business", "사업분야"), ("process", "제조공정"), ("equipment", "제조설비"), ("products", "취급품목")]),
    ("견적문의", "도면과 수량을 알려 주시면 검토 후 견적을 드립니다.",
     [("quote", "견적문의")]),
    ("고객센터", "궁금한 점이 있으시면 언제든지 연락 주십시오.",
     [("notice", "공지사항")]),
]

# 선 아이콘 (64x64). class="ac" 는 강조색 채움, class="acs" 는 강조색 선.
_IC = {
    "chip": '<rect x="18" y="18" width="28" height="28" rx="3"/><rect class="ac" x="25" y="25" width="14" height="14" rx="2"/><path d="M25 18v-8M32 18v-8M39 18v-8M25 54v-8M32 54v-8M39 54v-8M18 25h-8M18 32h-8M18 39h-8M54 25h-8M54 32h-8M54 39h-8"/>',
    "iron": '<path d="M36 28 50 14a4.2 4.2 0 0 1 6 6L42 34"/><path d="M36 28l-5 5 6 6 5-5"/><path d="M31 33 15 49"/><path d="M6 58h24"/><circle class="ac" cx="13" cy="51" r="4"/>',
    "inspect": '<circle cx="27" cy="27" r="16"/><path d="M39 39l15 15"/><path class="acs" d="M20 27l5 5 9-10"/>',
    "truck": '<path d="M5 16h32v28H5z"/><path d="M37 24h13l9 11v9H37z"/><circle cx="15" cy="47" r="5"/><circle cx="48" cy="47" r="5"/>',
    "doc": '<path d="M15 6h24l11 11v41H15z"/><path d="M39 6v11h11"/><path d="M22 28h20M22 36h20M22 44h12"/>',
    "order": '<rect x="14" y="10" width="36" height="46" rx="3"/><path d="M24 10V6h16v4"/><path class="acs" d="M22 30l5 5 9-10"/><path d="M22 44h20"/>',
    "box": '<path d="M32 6 56 18v28L32 58 8 46V18z"/><path d="M8 18l24 12 24-12M32 30v28"/>',
    "pack": '<rect x="8" y="24" width="48" height="32" rx="2"/><path d="M4 16h56v8H4z"/><path class="acs" d="M32 16v40"/><path d="M32 16c-6-10-16-8-14-2s14 2 14 2c6-10 16-8 14-2s-14 2-14 2"/>',
}
SVG = {
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></svg>',
    "kakao": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3.5c-5.2 0-9.5 3.3-9.5 7.4 0 2.6 1.7 4.9 4.3 6.2l-1 3.7c-.1.3.3.6.6.4l4.3-2.9c.4 0 .9.1 1.3.1 5.2 0 9.5-3.3 9.5-7.4S17.2 3.5 12 3.5z"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>',
}


def icon(name):
    return ('<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.8" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            + _IC[name].replace('class="ac"', 'fill="currentColor" stroke="none" opacity=".35"')
                       .replace('class="acs"', 'opacity=".55"')
            + "</svg>")


def kakao_href():
    return CO["kakao"] or "#kakao"


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
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&display=swap">
<link rel="stylesheet" href="style.css">
</head>
<body>
"""


def header(group):
    items, smap = [], ""
    for g, _, pages in MENU:
        links = "".join('<a href="%s.html">%s</a>' % (k, t) for k, t in pages)
        many = len(pages) > 1
        items.append('<li%s><a href="%s.html">%s</a>%s</li>' % (
            ' class="on"' if g == group else "", pages[0][0], g, f'<div class="sub">{links}</div>' if many else ""))
        smap += (f'<dl><dt><a href="{pages[0][0]}.html">{g}</a></dt>'
                 + (f"<dd>{links}</dd>" if many else "") + "</dl>")
    return f"""<header class="header">
  <div class="wrap">
    <a class="logo" href="index.html"><strong>삼은테크</strong><small>SAMEUN TECH</small></a>
    <ul class="gnb">{"".join(items)}</ul>
    <button type="button" class="menu-btn" id="menuOpen" aria-label="전체 메뉴" aria-expanded="false" aria-controls="sitemap">{SVG["menu"]}</button>
  </div>
</header>
<div class="sitemap" id="sitemap"><div class="sitemap-inner">
  <button type="button" class="sitemap-close" id="menuClose" aria-label="메뉴 닫기">&times;</button>
  <dl><dt><a href="index.html">처음으로</a></dt></dl>{smap}
</div></div>
"""


def sub_frame(group, key):
    slogan, pages = next((s, p) for g, s, p in MENU if g == group)
    tabs = "".join('<li%s><a href="%s.html">%s</a></li>' % (' class="on"' if k == key else "", k, t)
                   for k, t in pages)
    return f"""<div class="svisual">
  <div class="wrap"><h2>{group}</h2><p>{slogan}</p></div>
  <div class="ph dark">배너 사진 자리</div>
</div>
<nav class="tabs" aria-label="{group} 메뉴"><ul>{tabs}</ul></nav>
"""


def footer():
    c = CO
    return f"""<footer class="footer">
  <div class="wrap">
    <b>{c["name"]}</b><br>
    <span>주소 : {c["addr"]}</span><span>대표 : {c["ceo"]}</span><span>사업자등록번호 : {c["bizno"]}</span><br>
    <span>TEL : {c["tel"]}</span><span>E-Mail : <a href="mailto:{c["email"]}">{c["email"]}</a></span><br>
    COPYRIGHT &copy; 삼은테크. ALL RIGHTS RESERVED.
  </div>
</footer>
<a class="kakao-float" href="{kakao_href()}" target="_blank" rel="noopener" aria-label="카카오톡 문의">{SVG["kakao"]}<span>카카오톡 문의</span></a>
<script src="site.js"></script>
</body>
</html>
"""


def fill(body):
    body = re.sub(r"\{\{ICON_(\w+)\}\}", lambda m: icon(m.group(1)), body)
    body = re.sub(r"\{\{SVG_(\w+)\}\}", lambda m: SVG[m.group(1)], body)
    body = body.replace("{{kakao_href}}", kakao_href())
    for k, v in CO.items():
        body = body.replace("{{" + k + "}}", v)
    if "{{" in body:
        raise SystemExit("unfilled placeholder: " + body[body.index("{{"):][:40])
    return body


def main():
    text = (HERE / "content.html").read_text(encoding="utf-8")
    parts = re.split(r"^<!-- @page (\w+) -->[ \t]*$", text, flags=re.M)
    bodies = {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}
    group_of = {k: (g, t) for g, _, pages in MENU for k, t in pages}
    missing = (set(group_of) | {"index"}) - set(bodies)
    if missing:
        raise SystemExit(f"content.html 에 없는 페이지: {sorted(missing)}")

    desc = "삼은테크는 2007년부터 경기도 광명에서 SMT 실장, 수삽, PCB 조립을 해 온 전자부품 제조 기업입니다."
    out = {"index": head("삼은테크 | SMT · 수삽 · PCB 조립", desc) + header(None)
           + "<main>\n" + fill(bodies["index"]) + "\n</main>\n" + footer()}
    for key, (group, title) in group_of.items():
        out[key] = (head(f"{title} | 삼은테크", desc) + header(group) + sub_frame(group, key)
                    + f'<main class="content"><div class="wrap">\n<h3 class="c-title">{title}</h3>\n'
                    + fill(bodies[key]) + "\n</div></main>\n" + footer())
    for key, html in out.items():
        (OUT / f"{key}.html").write_text(html, encoding="utf-8", newline="\n")
    # 메뉴에서 빠진 옛 페이지 정리
    stale = [p.name for p in OUT.glob("*.html") if p.stem not in out]
    for name in stale:
        (OUT / name).unlink()
    print("built", len(out), "pages:", ", ".join(out), "| removed:", ", ".join(stale) or "-")


if __name__ == "__main__":
    main()
