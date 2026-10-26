/* پنل «رنگ اجزای سایت»: هماهنگی متن رنگ ↔ انتخابگر رنگ ↔ نمونه‌ی زنده ↔ دکمه‌ی پیش‌فرض.
   فقط مقدارهای معتبر روی نمونه اعمال می‌شود؛ اعتبارسنجی نهایی در سرور انجام می‌شود. */
(function () {
  'use strict';
  var HEX = /^#(?:[0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})$/i;
  var RGB = /^rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(?:,\s*(?:0|1|0?\.\d{1,3}|1\.0{1,3})\s*)?\)$/i;

  function isValid(v) {
    if (!v) return true;
    if (v.toLowerCase() === 'transparent' || HEX.test(v)) return true;
    var m = RGB.exec(v);
    return !!m && Math.max(+m[1], +m[2], +m[3]) <= 255;
  }
  function two(n) { n = Math.max(0, Math.min(255, n)); return (n < 16 ? '0' : '') + n.toString(16); }
  function toHex6(v) {
    if (!v) return null;
    var m;
    if (HEX.test(v)) {
      var d = v.slice(1);
      if (d.length === 3) d = d.charAt(0) + d.charAt(0) + d.charAt(1) + d.charAt(1) + d.charAt(2) + d.charAt(2);
      return '#' + d.slice(0, 6).toLowerCase();
    }
    m = RGB.exec(v);
    if (m) return '#' + two(+m[1]) + two(+m[2]) + two(+m[3]);
    return null;
  }

  function init(box) {
    var text = box.querySelector('.garnet-color-text');
    var picker = box.querySelector('.garnet-color-picker');
    var swatch = box.querySelector('.garnet-color-swatch i');
    var reset = box.querySelector('.garnet-color-reset');
    if (!text || !picker || !swatch) return;
    var fallback = box.getAttribute('data-default') || '';

    function sync() {
      var v = text.value.trim();
      var ok = isValid(v);
      text.classList.toggle('garnet-color-invalid', !ok);
      box.classList.toggle('is-default', !v);
      var shown = v && ok ? v : fallback;
      swatch.style.background = shown;
      var hex = toHex6(shown);
      if (hex) picker.value = hex;
    }
    text.addEventListener('input', sync);
    text.addEventListener('change', sync);
    picker.addEventListener('input', function () { text.value = picker.value; sync(); });
    if (reset) reset.addEventListener('click', function () { text.value = ''; sync(); text.focus(); });
    sync();
  }

  function boot() { Array.prototype.forEach.call(document.querySelectorAll('.garnet-color'), init); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
