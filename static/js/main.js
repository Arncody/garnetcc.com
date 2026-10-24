document.addEventListener('DOMContentLoaded', () => {
  const navToggle = document.getElementById('nav-toggle');
  const nav = document.getElementById('main-nav');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const closeNav = () => {
    if (!nav || !navToggle) return;
    nav.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
  };

  if (navToggle && nav) {
    navToggle.addEventListener('click', (event) => {
      event.stopPropagation();
      const open = nav.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', String(open));
    });
    nav.querySelectorAll('a').forEach((a) => a.addEventListener('click', closeNav));
    document.addEventListener('click', (event) => {
      if (nav.classList.contains('open') && !nav.contains(event.target) && !navToggle.contains(event.target)) closeNav();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeNav();
    });
  }

  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (event) => {
      const id = a.getAttribute('href');
      if (!id || id.length <= 1) return;
      const target = document.querySelector(id);
      if (!target) return;
      event.preventDefault();
      target.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
      closeNav();
    });
  });

  window.addEventListener('scroll', () => {
    document.querySelector('.g-header')?.classList.toggle('scrolled', window.scrollY > 16);
  }, { passive: true });

  document.querySelectorAll('.site-toast').forEach((toast) => {
    window.setTimeout(() => {
      toast.style.transition = 'opacity .25s ease, transform .25s ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-6px)';
      window.setTimeout(() => toast.remove(), 280);
    }, 5200);
  });

  // Consultation modal: one authoritative state machine, no native dialog/open attribute.
  const modal = document.getElementById('consultModal');
  if (!modal) return;
  if (modal.parentElement !== document.body) document.body.appendChild(modal);
  const closer = modal.querySelector('[data-consult-close]');
  const form = modal.querySelector('[data-consult-form]');
  const panel = modal.querySelector('.consult-modal-inner');
  let previousFocus = null;
  let previousOverflow = '';
  let previousHtmlOverflow = '';
  let isOpen = false;

  const updateViewport = () => {
    if (!isOpen) return;
    const viewport = window.visualViewport;
    // visualViewport.height changes when iOS keyboard opens; offsetTop is not
    // added to the fixed overlay to avoid the double-offset Safari issue.
    const height = viewport ? viewport.height : window.innerHeight;
    modal.style.setProperty('--consult-vh', `${Math.max(240, height)}px`);
  };
  const setModalState = (open) => {
    isOpen = open;
    modal.hidden = !open;
    if (open) modal.removeAttribute('hidden');
    else modal.setAttribute('hidden', '');
    modal.classList.toggle('is-open', open);
    modal.setAttribute('aria-hidden', String(!open));
    modal.removeAttribute('open'); // DIV is not a native dialog.
    document.body.classList.toggle('modal-open', open);
  };
  const openModal = () => {
    if (isOpen) return;
    closeNav();
    previousFocus = document.activeElement;
    previousOverflow = document.body.style.overflow;
    previousHtmlOverflow = document.documentElement.style.overflow;
    setModalState(true);
    document.body.style.overflow = 'hidden';
    document.documentElement.style.overflow = 'hidden';
    updateViewport();
    if (panel) panel.scrollTop = 0;
    // Focus the dialog container, not a text input: don't trigger iOS keyboard.
    try { modal.focus({ preventScroll: true }); } catch (_) { modal.focus(); }
  };
  const closeModal = () => {
    if (!isOpen) return;
    if (modal.contains(document.activeElement) && document.activeElement.blur) document.activeElement.blur();
    setModalState(false);
    document.body.style.overflow = previousOverflow;
    document.documentElement.style.overflow = previousHtmlOverflow;
    if (previousFocus?.isConnected) {
      try { previousFocus.focus({ preventScroll: true }); } catch (_) { previousFocus.focus(); }
    }
  };
  // One delegated click handler for every consultation / pre-purchase trigger.
  document.addEventListener('click', (event) => {
    const target = event.target instanceof Element ? event.target : event.target?.parentElement;
    const trigger = target?.closest('[data-consult-open]');
    if (!trigger) return;
    event.preventDefault();
    openModal();
  });
  closer?.addEventListener('click', closeModal);
  modal.addEventListener('click', (event) => { if (event.target === modal) closeModal(); });
  document.addEventListener('keydown', (event) => {
    if (!isOpen) return;
    if (event.key === 'Escape') { event.preventDefault(); closeModal(); return; }
    if (event.key !== 'Tab') return;
    const focusable = [...modal.querySelectorAll('button:not([disabled]), input:not([disabled]):not([type="hidden"]), textarea:not([disabled]), select:not([disabled]), a[href]')].filter(el => el.getClientRects().length);
    if (!focusable.length) { event.preventDefault(); modal.focus(); return; }
    const first = focusable[0], last = focusable[focusable.length - 1];
    if (event.shiftKey && (document.activeElement === first || document.activeElement === modal)) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });
  window.visualViewport?.addEventListener('resize', updateViewport);
  window.visualViewport?.addEventListener('scroll', updateViewport);
  window.addEventListener('resize', updateViewport);
  window.addEventListener('orientationchange', updateViewport);
  setModalState(false);
  // Preserve the user's inputs when server-side form validation fails.
  if (modal.dataset.autoOpen === 'true' || modal.classList.contains('has-form-errors')) openModal();

  // Friendly client-side validation: no page navigation and errors stay beside the field.
  if (form) {
    const clearInvalid = (field) => {
      field.classList.remove('is-invalid');
      const old = field.parentElement?.querySelector('.client-field-error');
      old?.remove();
    };
    const markInvalid = (field, message) => {
      clearInvalid(field);
      field.classList.add('is-invalid');
      const error = document.createElement('div');
      error.className = 'field-error client-field-error';
      error.textContent = message;
      field.parentElement?.appendChild(error);
    };

    form.querySelectorAll('input, textarea, select').forEach((field) => {
      field.addEventListener('input', () => clearInvalid(field));
      field.addEventListener('change', () => clearInvalid(field));
    });

    form.addEventListener('submit', (event) => {
      let firstInvalid = null;
      const langEn = document.documentElement.lang === 'en';
      const name = form.querySelector('[name="name"]');
      const phone = form.querySelector('[name="phone"]');
      const subject = form.querySelector('[name="subject"]');
      const gender = form.querySelector('input[name="gender"]:checked');
      const genderWrap = form.querySelector('.gender-options');

      const requireText = (field, message) => {
        if (!field || field.value.trim().length < 2) {
          if (field) markInvalid(field, message);
          if (!firstInvalid) firstInvalid = field;
        }
      };
      requireText(name, langEn ? 'Please enter your full name.' : 'لطفاً نام و نام‌خانوادگی را وارد کنید.');
      if (!phone || !/^(?:0?9\d{9}|\+?98\d{10})$/.test(phone.value.replace(/[\s-]/g, ''))) {
        if (phone) markInvalid(phone, langEn ? 'Please enter a valid phone number.' : 'لطفاً یک شماره تماس معتبر وارد کنید.');
        if (!firstInvalid) firstInvalid = phone;
      }
      if (!gender) {
        if (genderWrap) {
          genderWrap.classList.add('is-invalid');
          const old = genderWrap.parentElement?.querySelector('.client-field-error');
          old?.remove();
          const error = document.createElement('div');
          error.className = 'field-error client-field-error';
          error.textContent = langEn ? 'Please choose an option.' : 'لطفاً یکی از گزینه‌ها را انتخاب کنید.';
          genderWrap.parentElement?.appendChild(error);
        }
        if (!firstInvalid) firstInvalid = genderWrap;
      }
      requireText(subject, langEn ? 'Please enter the subject of your request.' : 'لطفاً موضوع درخواست را وارد کنید.');

      if (firstInvalid) {
        event.preventDefault();
        openModal();
        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
        if (typeof firstInvalid.focus === 'function') firstInvalid.focus({ preventScroll: true });
      }
    });
  }
});

/* حفاظت سمت‌مرورگر از عکس/ویدیو (کنار حفاظت سمت‌سرور در website/media_views.py) */
(function () {
  document.addEventListener('contextmenu', function (e) {
    var t = e.target;
    if (t && (t.tagName === 'IMG' || t.tagName === 'VIDEO')) e.preventDefault();
  });
  document.addEventListener('dragstart', function (e) {
    var t = e.target;
    if (t && (t.tagName === 'IMG' || t.tagName === 'VIDEO')) e.preventDefault();
  });
  document.querySelectorAll('video').forEach(function (v) {
    v.setAttribute('controlsList', 'nodownload noremoteplayback');
    v.setAttribute('disablePictureInPicture', '');
    v.disableRemotePlayback = true;
  });
})();

/* ---------- ردیف افقی چرخان پروژه‌ها (Vanilla JS) ----------
   - سرعت از پنل ادمین (data-speed، پیکسل بر ثانیه)
   - با لمس/کشیدن/هاور متوقف می‌شود و بعد از چند ثانیه ادامه می‌دهد
   - با prefers-reduced-motion فقط قابل اسکرول دستی است */
(function () {
  var rails = document.querySelectorAll('[data-rail]');
  if (!rails.length) return;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  rails.forEach(function (rail) {
    var track = rail.querySelector('[data-rail-track]');
    if (!track) return;
    var originals = Array.prototype.slice.call(track.children);
    if (originals.length < 2) return;
    var speed = Math.max(10, Math.min(200, parseInt(rail.getAttribute('data-speed'), 10) || 40));
    var dirSign = 1, setWidth = 0, pos = 0, last = 0, paused = false, resumeTimer = null, dragging = false;
    var startX = 0, startPos = 0, moved = false, visible = true;

    function build() {
      Array.prototype.slice.call(track.querySelectorAll('[data-clone]')).forEach(function (n) { n.remove(); });
      var gap = parseFloat(getComputedStyle(track).columnGap || getComputedStyle(track).gap) || 0;
      var r0 = originals[0].getBoundingClientRect(), rN = originals[originals.length - 1].getBoundingClientRect();
      setWidth = Math.abs(dirSign < 0 ? r0.right - rN.left : rN.right - r0.left) + gap;
      var need = Math.ceil((rail.clientWidth * 2) / Math.max(setWidth, 1)) + 1;
      for (var i = 0; i < need; i++) {
        originals.forEach(function (card) {
          var c = card.cloneNode(true);
          c.setAttribute('data-clone', '1');
          c.setAttribute('aria-hidden', 'true');
          c.setAttribute('tabindex', '-1');
          track.appendChild(c);
        });
      }
    }

    function wrap() {
      if (!setWidth) return;
      if (pos >= setWidth) { pos -= setWidth; rail.scrollLeft = dirSign * pos; }
      else if (pos < 0) { pos += setWidth; rail.scrollLeft = dirSign * pos; }
    }

    function tick(now) {
      if (!last) last = now;
      var dt = Math.min(64, now - last);
      last = now;
      if (!paused && !dragging && visible && !reduce && !document.hidden) {
        pos += speed * dt / 1000;
        wrap();
        rail.scrollLeft = dirSign * pos;
      }
      window.requestAnimationFrame(tick);
    }

    function pause() { paused = true; window.clearTimeout(resumeTimer); }
    function resume(delay) {
      window.clearTimeout(resumeTimer);
      resumeTimer = window.setTimeout(function () { pos = dirSign * rail.scrollLeft; paused = false; }, delay || 0);
    }

    // اسکرول دستی (لمس یا چرخ ماوس): موقعیت را همگام کن و کمی بعد ادامه بده
    rail.addEventListener('scroll', function () {
      if (paused || dragging) { pos = dirSign * rail.scrollLeft; wrap(); }
    }, { passive: true });
    rail.addEventListener('mouseenter', pause);
    rail.addEventListener('mouseleave', function () { if (!dragging) resume(300); });
    rail.addEventListener('focusin', pause);
    rail.addEventListener('focusout', function () { resume(600); });
    rail.addEventListener('touchstart', pause, { passive: true });
    rail.addEventListener('touchend', function () { resume(2500); }, { passive: true });
    rail.addEventListener('wheel', function () { pause(); resume(1800); }, { passive: true });

    // کشیدن با ماوس
    rail.addEventListener('pointerdown', function (e) {
      if (e.pointerType !== 'mouse' || e.button !== 0) return;
      dragging = true; moved = false; startX = e.clientX; startPos = dirSign * rail.scrollLeft; pos = startPos;
    });
    window.addEventListener('pointermove', function (e) {
      if (!dragging) return;
      var dx = e.clientX - startX;
      if (Math.abs(dx) > 4) { moved = true; rail.classList.add('is-dragging'); }
      if (moved) { pos = startPos - dirSign * dx; wrap(); rail.scrollLeft = dirSign * pos; }
    });
    window.addEventListener('pointerup', function () {
      if (!dragging) return;
      dragging = false; rail.classList.remove('is-dragging');
      pos = dirSign * rail.scrollLeft;
    });
    rail.addEventListener('click', function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) { visible = entries[0].isIntersecting; }).observe(rail);
    }

    var resizeTimer = null;
    window.addEventListener('resize', function () {
      window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(function () { build(); pos = dirSign * rail.scrollLeft; wrap(); }, 200);
    });

    function init() {
      // Keep the scroll container LTR so scrollLeft behaves consistently in iOS Safari/RTL pages.
      rail.style.direction = 'ltr';
      track.style.direction = getComputedStyle(document.documentElement).direction === 'rtl' ? 'rtl' : 'ltr';
      dirSign = 1;
      build();
      pos = 0;
      rail.scrollLeft = 0;
      window.requestAnimationFrame(tick);
    }
    if (document.readyState === 'complete') init(); else window.addEventListener('load', init);
  });
})();
