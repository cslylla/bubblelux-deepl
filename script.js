function attachSwitcher() {
    const select = document.getElementById('lang-select');
    if (!select) return;

    select.addEventListener('change', async function (e) {
      const selected = e.target.value;

      // Show loader for any language change
      const loader = document.getElementById('lang-loader');
      if (loader) loader.style.display = 'flex';

      if (selected === 'en') {
        window.location.replace('/');
        return;
      }

      try {
        const res = await fetch('http://localhost:5000/translate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ target_lang: 'DE' }),
        });

        const html = await res.text();
        document.documentElement.innerHTML = html;
        const billed = res.headers.get('X-Billed-Characters');
        if (billed) console.log(`DeepL billed characters: ${billed}`);

        setTimeout(function () {
          const loader = document.getElementById('lang-loader');
          if (loader) loader.style.display = 'none';
          const newSelect = document.getElementById('lang-select');
          if (newSelect) newSelect.value = 'de';
          attachSwitcher();
        }, 100);

      } catch (err) {
        if (loader) loader.style.display = 'none';
        console.error('Translation failed:', err);
      }
    });
  }

  attachSwitcher();
