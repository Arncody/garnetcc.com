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

/* ---------- Garnet project marquee: robust transform animation ----------
   Uses measured card widths (not RTL-dependent left/right arithmetic).
   Rebuilds clones after images/fonts/layout settle and animates continuously. */
(function () {
  'use strict';
  function initProjectRails() {
    document.querySelectorAll('[data-rail]').forEach(function (rail) {
      var track = rail.querySelector('[data-rail-track]');
      if (!track || rail.dataset.railReady === '1') return;
      var originals = Array.prototype.slice.call(track.children).filter(function (el) {
        return el.getAttribute('data-clone') !== '1';
      });
      if (originals.length < 2) return;

      rail.dataset.railReady = 'initializing';
      var speed = Math.max(12, Math.min(100, Number(rail.getAttribute('data-speed')) || 28));
      var pos = 0, setWidth = 0, lastTime = 0, rafId = 0;
      var paused = false, dragging = false, visible = true, startX = 0, startPos = 0;
      var resumeTimer = 0, resizeTimer = 0, moved = false;
      var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      function clearClones() {
        track.querySelectorAll('[data-clone="1"]').forEach(function (node) { node.remove(); });
      }
      function measureOriginalSet() {
        var style = window.getComputedStyle(track);
        var gap = parseFloat(style.columnGap || style.gap) || 0;
        var total = 0;
        originals.forEach(function (card) { total += card.getBoundingClientRect().width; });
        total += gap * Math.max(0, originals.length - 1);
        return total;
      }
      function build() {
        clearClones();
        track.style.willChange = 'transform';
        track.style.flexWrap = 'nowrap';
        track.style.width = 'max-content';
        setWidth = measureOriginalSet();
        if (!setWidth || !rail.clientWidth) {
          rail.dataset.railReady = '0';
          return false;
        }
        // Add whole sets until the track can cover the viewport during the loop.
        var currentWidth = track.scrollWidth;
        var safety = 0;
        while (currentWidth < rail.clientWidth + setWidth && safety < 20) {
          originals.forEach(function (card) {
            var clone = card.cloneNode(true);
            clone.setAttribute('data-clone', '1');
            clone.setAttribute('aria-hidden', 'true');
            clone.querySelectorAll('a,button,input,select,textarea,[tabindex]').forEach(function (el) {
              el.setAttribute('tabindex', '-1');
            });
            track.appendChild(clone);
          });
          currentWidth = track.scrollWidth;
          safety++;
        }
        pos = ((pos % setWidth) + setWidth) % setWidth;
        render();
        rail.dataset.railReady = '1';
        return true;
      }
      function render() {
        track.style.transform = 'translate3d(' + (-pos) + 'px,0,0)';
      }
      function tick(now) {
        if (!lastTime) lastTime = now;
        var dt = Math.min(50, Math.max(0, now - lastTime));
        lastTime = now;
        if (!reduceMotion && !paused && !dragging && visible && !document.hidden && setWidth > 0) {
          pos += speed * dt / 1000;
          if (pos >= setWidth) pos -= setWidth * Math.floor(pos / setWidth);
          render();
        }
        rafId = window.requestAnimationFrame(tick);
      }
      function pause() { paused = true; window.clearTimeout(resumeTimer); }
      function resume(delay) {
        window.clearTimeout(resumeTimer);
        resumeTimer = window.setTimeout(function () { paused = false; lastTime = 0; }, delay || 0);
      }
      rail.addEventListener('mouseenter', pause);
      rail.addEventListener('mouseleave', function () { if (!dragging) resume(350); });
      rail.addEventListener('focusin', pause);
      rail.addEventListener('focusout', function () { resume(700); });
      rail.addEventListener('touchstart', function (e) {
        if (!e.touches || !e.touches.length) return;
        pause(); dragging = true; startX = e.touches[0].clientX; startPos = pos; moved = false;
      }, { passive: true });
      rail.addEventListener('touchmove', function (e) {
        if (!dragging || !e.touches || !e.touches.length || !setWidth) return;
        var dx = e.touches[0].clientX - startX;
        if (Math.abs(dx) > 5) moved = true;
        if (moved) { pos = ((startPos - dx) % setWidth + setWidth) % setWidth; render(); }
      }, { passive: true });
      rail.addEventListener('touchend', function () { dragging = false; resume(1200); }, { passive: true });
      rail.addEventListener('touchcancel', function () { dragging = false; resume(800); }, { passive: true });
      rail.addEventListener('wheel', function () { pause(); resume(1200); }, { passive: true });
      rail.addEventListener('click', function (e) {
        if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; }
      }, true);
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (entries) { visible = !!entries[0].isIntersecting; }).observe(rail);
      }
      function scheduleBuild() {
        window.clearTimeout(resizeTimer);
        resizeTimer = window.setTimeout(function () { build(); lastTime = 0; }, 180);
      }
      window.addEventListener('resize', scheduleBuild);
      if ('ResizeObserver' in window) new ResizeObserver(scheduleBuild).observe(rail);
      // Wait for images to load because image/layout dimensions can change after DOM ready.
      var images = originals.reduce(function (all, card) {
        return all.concat(Array.prototype.slice.call(card.querySelectorAll('img')));
      }, []);
      Promise.all(images.map(function (img) {
        if (img.complete) return Promise.resolve();
        return new Promise(function (resolve) {
          img.addEventListener('load', resolve, { once: true });
          img.addEventListener('error', resolve, { once: true });
        });
      })).then(function () {
        build();
        window.requestAnimationFrame(function () { build(); lastTime = 0; });
      });
      if (!rafId) rafId = window.requestAnimationFrame(tick);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initProjectRails, { once: true });
  else initProjectRails();
})();
