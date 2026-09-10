// extras.js — copy-to-clipboard buttons and image lightbox.
(function () {
  'use strict';

  function initCopyButtons() {
    var pres = document.querySelectorAll('.writing-body pre');
    pres.forEach(function (pre) {
      if (pre.querySelector('.copy-btn')) return;
      var codeEl = pre.querySelector('code') || pre;
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'copy-btn';
      btn.textContent = 'Copy';
      btn.addEventListener('click', function () {
        var text = codeEl.textContent || '';
        var done = function () {
          btn.textContent = 'Copied';
          btn.classList.add('copied');
          setTimeout(function () {
            btn.textContent = 'Copy';
            btn.classList.remove('copied');
          }, 1500);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done, done);
        } else {
          var ta = document.createElement('textarea');
          ta.value = text;
          ta.style.position = 'fixed';
          ta.style.opacity = '0';
          document.body.appendChild(ta);
          ta.select();
          try { document.execCommand('copy'); } catch (e) {}
          document.body.removeChild(ta);
          done();
        }
      });
      pre.appendChild(btn);
    });
  }

  var overlay = null;

  function closeLightbox() {
    if (overlay) {
      overlay.remove();
      overlay = null;
      document.removeEventListener('keydown', onKeydown);
    }
  }

  function onKeydown(e) {
    if (e.key === 'Escape') closeLightbox();
  }

  function openLightbox(src, alt) {
    closeLightbox();
    overlay = document.createElement('div');
    overlay.className = 'lightbox-overlay';
    var img = document.createElement('img');
    img.src = src;
    img.alt = alt || '';
    overlay.appendChild(img);
    overlay.addEventListener('click', closeLightbox);
    document.body.appendChild(overlay);
    document.addEventListener('keydown', onKeydown);
  }

  function initLightbox() {
    var imgs = document.querySelectorAll('.writing-body figure.wide img');
    imgs.forEach(function (img) {
      img.addEventListener('click', function () {
        var visible = img;
        if (getComputedStyle(img).display === 'none') {
          var fig = img.closest('figure');
          var other = fig && fig.querySelector('img.img-light, img.img-dark');
          if (other && getComputedStyle(other).display !== 'none') visible = other;
        }
        openLightbox(visible.currentSrc || visible.src, visible.alt);
      });
    });
  }

  function init() {
    initCopyButtons();
    initLightbox();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
