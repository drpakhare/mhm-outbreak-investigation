// Light by default. The switch stores the visitor's choice in this browser only.
(function () {
  var KEY = 'mhm-theme', root = document.documentElement;
  function get() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function set(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function apply(v) { root.setAttribute('data-theme', v === 'dark' ? 'dark' : 'light'); }
  apply(get());
  document.addEventListener('DOMContentLoaded', function () {
    var host = document.querySelector('header.band > div'); if (!host) return;
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'theme-toggle'; b.id = 'theme-toggle';
    function label() {
      var dark = root.getAttribute('data-theme') === 'dark';
      b.textContent = dark ? 'Light' : 'Dark';
      b.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
    }
    b.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      apply(next); set(next); label();
    });
    label(); host.appendChild(b);
  });
})();
