// Client-side search for Evan's Writings.
// No dependencies. Searches title, description, collection, and tags
// using the data-* attributes on each .writing-list-item element.
// Supports /writings/?q=search+term URL parameter.

(function () {
  'use strict';

  var input = document.getElementById('search-input');
  var list = document.getElementById('writing-list');
  var count = document.getElementById('search-count');
  var noResults = document.getElementById('search-no-results');
  if (!input || !list) return;

  var items = Array.prototype.slice.call(list.querySelectorAll('.writing-list-item'));
  var total = items.length;

  function search(query) {
    query = query.trim().toLowerCase();
    var terms = query.length > 0 ? query.split(/\s+/) : [];
    var visible = 0;

    for (var i = 0; i < items.length; i++) {
      var item = items[i];
      if (terms.length === 0) {
        item.style.display = '';
        visible++;
        continue;
      }
      var haystack = (
        item.getAttribute('data-title') + ' ' +
        item.getAttribute('data-description') + ' ' +
        item.getAttribute('data-collection') + ' ' +
        item.getAttribute('data-tags')
      );
      var match = true;
      for (var j = 0; j < terms.length; j++) {
        if (haystack.indexOf(terms[j]) === -1) {
          match = false;
          break;
        }
      }
      if (match) {
        item.style.display = '';
        visible++;
      } else {
        item.style.display = 'none';
      }
    }

    if (count) {
      if (terms.length === 0) {
        count.textContent = '';
      } else {
        count.textContent = visible + ' of ' + total + ' writings';
      }
    }
    if (noResults) {
      noResults.style.display = visible === 0 ? '' : 'none';
    }
  }

  // Read ?q= from URL on load
  var urlParams = new URLSearchParams(window.location.search);
  var initialQuery = urlParams.get('q') || '';
  if (initialQuery) {
    input.value = initialQuery;
    search(initialQuery);
  }

  // Live search on input
  var debounceTimer;
  input.addEventListener('input', function () {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function () {
      search(input.value);
      // Update URL without scrolling
      var url = new URL(window.location.href);
      if (input.value.trim()) {
        url.searchParams.set('q', input.value.trim());
      } else {
        url.searchParams.delete('q');
      }
      window.history.replaceState(null, '', url);
    }, 150);
  });

  // Focus on '/' key (keyboard shortcut)
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== input) {
      e.preventDefault();
      input.focus();
    }
  });
})();
