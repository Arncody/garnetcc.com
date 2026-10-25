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

/* ---------- Seamless project marquee (transform-based for iOS Safari + RTL) ----------
   Avoids scrollLeft because its RTL semantics differ across Safari/iOS versions. */
(function () {
  function initRails() {
    var rails = document.querySelectorAll('[data-rail]');
    if (!rails.length) return;
    /* Set RESPECT_REDUCED_MOTION=true to stop auto-scroll for visitors whose OS has "Reduce Motion" on (manual drag still works). */
    var RESPECT_REDUCED_MOTION = false;
    var reduceMotion = RESPECT_REDUCED_MOTION && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    /* Hover-pause only for real mouse devices: touch browsers emulate mouseenter on tap and would leave the rail paused forever. */
    var canHover = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;

    rails.forEach(function (rail) {
      var track = rail.querySelector('[data-rail-track]');
      if (!track || rail.dataset.railReady === '1') return;
      var originals = Array.prototype.slice.call(track.children);
      if (originals.length < 2) return;
      rail.dataset.railReady = '1';
      var speed = Math.max(10, Math.min(200, parseInt(rail.getAttribute('data-speed'), 10) || 32));
      var setWidth = 0, pos = 0, last = 0, paused = false, dragging = false;
      var visible = true, resumeTimer = null, startX = 0, startPos = 0, moved = false;

      function removeClones() {
        Array.prototype.slice.call(track.querySelectorAll('[data-clone="1"]')).forEach(function (node) { node.remove(); });
      }
      function measureSet() {
        if (!originals.length) return 0;
        var first = originals[0].getBoundingClientRect();
        var lastCard = originals[originals.length - 1].getBoundingClientRect();
        var gap = parseFloat(getComputedStyle(track).columnGap || getComputedStyle(track).gap) || 0;
        return Math.max(0, lastCard.right - first.left + gap);
      }
      function build() {
        removeClones();
        setWidth = measureSet();
        if (!setWidth) return;
        // Ensure the duplicated content always covers the visible viewport at every loop point.
        var safety = 0;
        while (track.scrollWidth < rail.clientWidth + setWidth && safety < 8) {
          originals.forEach(function (card) {
            var clone = card.cloneNode(true);
            clone.setAttribute('data-clone', '1');
            clone.setAttribute('aria-hidden', 'true');
            clone.querySelectorAll('a,button,input,select,textarea,[tabindex]').forEach(function (el) {
              el.setAttribute('tabindex', '-1');
            });
            track.appendChild(clone);
          });
          safety++;
        }
        pos = pos % setWidth;
        render();
      }
      function render() {
        track.style.transform = 'translate3d(' + (-pos) + 'px,0,0)';
      }
      function tick(now) {
        if (!last) last = now;
        var dt = Math.min(50, now - last);
        last = now;
        if (!reduceMotion && !paused && !dragging && visible && !document.hidden && setWidth > 0) {
          pos += speed * dt / 1000;
          if (pos >= setWidth) pos = pos % setWidth;
          render();
        }
        window.requestAnimationFrame(tick);
      }
      function pause() { paused = true; window.clearTimeout(resumeTimer); }
      function resume(delay) {
        window.clearTimeout(resumeTimer);
        resumeTimer = window.setTimeout(function () { paused = false; last = 0; }, delay || 0);
      }
      if (canHover) {
        rail.addEventListener('mouseenter', pause);
        rail.addEventListener('mouseleave', function () { if (!dragging) resume(350); });
      }
      rail.addEventListener('focusin', function () { if (canHover) pause(); });
      rail.addEventListener('focusout', function () { resume(700); });
      function wrap(v) {
        if (!setWidth) return 0;
        v = v % setWidth;
        return v < 0 ? v + setWidth : v;
      }
      function beginDrag(x) { animId++; pause(); dragging = true; startX = x; startPos = pos; moved = false; }
      function moveDrag(x) {
        if (!dragging) return;
        var dx = x - startX;
        if (Math.abs(dx) > 5) moved = true;
        if (moved) { pos = wrap(startPos - dx); render(); } /* finger right => content right */
      }
      function endDrag(delay) { if (!dragging) return; dragging = false; resume(delay); }
      /* Touch (iOS + Android). touchcancel is essential: Android fires it when the browser takes over a vertical scroll. */
      rail.addEventListener('touchstart', function (e) {
        if (e.touches && e.touches.length) beginDrag(e.touches[0].clientX);
      }, { passive: true });
      rail.addEventListener('touchmove', function (e) {
        if (e.touches && e.touches.length) moveDrag(e.touches[0].clientX);
      }, { passive: true });
      rail.addEventListener('touchend', function () { endDrag(1800); }, { passive: true });
      rail.addEventListener('touchcancel', function () { endDrag(1200); }, { passive: true });
      /* Mouse drag (desktop) */
      rail.addEventListener('mousedown', function (e) {
        if (e.button !== 0) return;
        beginDrag(e.clientX);
        rail.classList.add('is-dragging');
      });
      window.addEventListener('mousemove', function (e) { moveDrag(e.clientX); });
      window.addEventListener('mouseup', function () {
        rail.classList.remove('is-dragging');
        endDrag(900);
      });
      /* Horizontal wheel / trackpad swipe scrolls the rail; vertical wheel still scrolls the page. */
      rail.addEventListener('wheel', function (e) {
        var dx = e.deltaX, dy = e.deltaY;
        if (e.shiftKey && !dx) { dx = dy; dy = 0; }
        if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 0) {
          e.preventDefault();
          pause();
          pos = wrap(pos + dx);
          render();
        } else {
          pause();
        }
        resume(1800);
      }, { passive: false });
      /* Prev / next buttons + arrow keys: smooth step of exactly one card. */
      var animId = 0;
      function stepSize() { return originals.length ? setWidth / originals.length : 0; }
      function glide(direction) {
        var step = stepSize();
        if (!step) return;
        pause();
        var from = pos, delta = direction * step, t0 = 0, id = ++animId;
        function frame(now) {
          if (id !== animId) return;
          if (!t0) t0 = now;
          var k = Math.min(1, (now - t0) / 420);
          var e = 1 - Math.pow(1 - k, 3);
          pos = wrap(from + delta * e);
          render();
          if (k < 1) window.requestAnimationFrame(frame);
          else resume(2500);
        }
        window.requestAnimationFrame(frame);
      }
      var wrapper = rail.parentElement;
      if (wrapper) {
        Array.prototype.forEach.call(wrapper.querySelectorAll('[data-rail-nav]'), function (btn) {
          btn.addEventListener('click', function (e) {
            e.preventDefault();
            glide(parseInt(btn.getAttribute('data-rail-nav'), 10) || 1);
          });
        });
      }
      rail.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight') { e.preventDefault(); glide(1); }
        else if (e.key === 'ArrowLeft') { e.preventDefault(); glide(-1); }
      });
      rail.addEventListener('click', function (e) {
        if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; }
      }, true);
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (entries) { visible = !!entries[0].isIntersecting; }).observe(rail);
      }
      var resizeTimer = null;
      window.addEventListener('resize', function () {
        window.clearTimeout(resizeTimer);
        resizeTimer = window.setTimeout(function () { build(); last = 0; }, 180);
      });
      if ('ResizeObserver' in window) new ResizeObserver(function () { build(); }).observe(rail);
      build();
      window.requestAnimationFrame(tick);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initRails);
  else initRails();
})();
