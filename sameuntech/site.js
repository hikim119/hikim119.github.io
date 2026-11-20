// 삼은테크 홈페이지 공통 스크립트: 전체 메뉴 열고 닫기, 견적의뢰 메일 보내기
(function () {
  var sitemap = document.getElementById('sitemap');
  var openBtn = document.getElementById('menuOpen');
  var closeBtn = document.getElementById('menuClose');
  function setOpen(open) {
    sitemap.classList.toggle('open', open);
    openBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    document.body.style.overflow = open ? 'hidden' : '';
  }
  openBtn.addEventListener('click', function () { setOpen(true); });
  closeBtn.addEventListener('click', function () { setOpen(false); });
  sitemap.addEventListener('click', function (e) { if (e.target === sitemap) setOpen(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setOpen(false); });

  // 견적의뢰: 서버 없이 메일 앱으로 넘긴다
  var form = document.getElementById('quoteForm');
  if (!form) return;
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var f = form.elements;
    var need = [['company', '회사명'], ['name', '담당자'], ['phone', '연락처']];
    for (var i = 0; i < need.length; i++) {
      var el = f[need[i][0]];
      if (!el.value.trim()) { alert(need[i][1] + '을(를) 입력해 주세요.'); el.focus(); return; }
    }
    var body = [
      '회사명: ' + f.company.value,
      '담당자: ' + f.name.value,
      '연락처: ' + f.phone.value,
      '이메일: ' + f.email.value,
      '작업 구분: ' + f.type.value,
      '수량: ' + f.qty.value,
      '',
      '요청 내용:',
      f.msg.value,
      '',
      '(거버 · BOM 파일이 있으면 첨부해 주세요)'
    ].join('\n');
    location.href = 'mailto:sameuntech@naver.com'
      + '?subject=' + encodeURIComponent('[견적의뢰] ' + f.company.value)
      + '&body=' + encodeURIComponent(body);
  });
})();
