// Product key request — points at YOUR_KEY_API_URL once deployed (e.g. an Azure Function).
  // Until that's set, it falls back to a local demo key so the flow is testable today.
  const KEY_API_URL = "YOUR_KEY_API_URL"; // e.g. https://gemmanode-keys.azurewebsites.net/api/request-key

  const keyForm = document.getElementById('keyForm');
  const keyStatus = document.getElementById('keyStatus');
  const keyResult = document.getElementById('keyResult');
  const keyValue = document.getElementById('keyValue');
  const keySubmit = document.getElementById('keySubmit');
  const keyCopy = document.getElementById('keyCopy');

  function demoKey(email) {
    const seed = Array.from(email).reduce((a, c) => a + c.charCodeAt(0), 0);
    const rnd = () => Math.floor((Math.sin(seed + Math.random() * 1000) * 10000) % 9000 + 1000);
    return `GNODE-${rnd()}-${rnd()}-${rnd()}`.replace(/-(-?\d{4})/g, (m, g) => '-' + Math.abs(parseInt(g)));
  }

  keyForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('keyEmail').value.trim();
    if (!email) return;
    keySubmit.disabled = true;
    keySubmit.textContent = 'Requesting…';
    keyStatus.textContent = '';
    keyStatus.className = 'key-status';
    keyResult.classList.remove('show');

    try {
      if (!KEY_API_URL || KEY_API_URL === "YOUR_KEY_API_URL") {
        // No backend wired yet — show a demo key locally so you can test the UI.
        await new Promise(r => setTimeout(r, 500));
        keyValue.textContent = demoKey(email);
        keyResult.classList.add('show');
        keyStatus.textContent = 'Demo mode — connect YOUR_KEY_API_URL to issue real keys.';
        keyStatus.className = 'key-status';
      } else {
        const res = await fetch(KEY_API_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email })
        });
        if (!res.ok) throw new Error('Request failed');
        const data = await res.json();
        keyValue.textContent = data.key || 'Key issued — check your email.';
        keyResult.classList.add('show');
        keyStatus.textContent = 'Key issued successfully.';
        keyStatus.className = 'key-status ok';
      }
    } catch (err) {
      keyStatus.textContent = 'Something went wrong. Please try again.';
      keyStatus.className = 'key-status error';
    } finally {
      keySubmit.disabled = false;
      keySubmit.textContent = 'Get key';
    }
  });

  keyCopy?.addEventListener('click', () => {
    navigator.clipboard.writeText(keyValue.textContent).then(() => {
      keyCopy.textContent = 'Copied!';
      setTimeout(() => keyCopy.textContent = 'Copy', 1500);
    });
  });

  // OAuth signup — replace these placeholder client IDs / redirect URIs once registered.
  const GITHUB_CLIENT_ID = "YOUR_GITHUB_OAUTH_CLIENT_ID";
  const GOOGLE_CLIENT_ID = "YOUR_GOOGLE_OAUTH_CLIENT_ID";
  const REDIRECT_URI = "https://gemmanode.vighnesh.me/signup/callback"; // update to match your registered redirect

  document.getElementById('githubSignup')?.addEventListener('click', () => {
    if (GITHUB_CLIENT_ID.startsWith('YOUR_')) {
      alert('GitHub sign-in isn\'t configured yet — set GITHUB_CLIENT_ID in app.js once you register the OAuth app.');
      return;
    }
    const url = `https://github.com/login/oauth/authorize?client_id=${GITHUB_CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&scope=read:user%20user:email`;
    window.location.href = url;
  });

  document.getElementById('googleSignup')?.addEventListener('click', () => {
    if (GOOGLE_CLIENT_ID.startsWith('YOUR_')) {
      alert('Google sign-in isn\'t configured yet — set GOOGLE_CLIENT_ID in app.js once you register the OAuth app.');
      return;
    }
    const url = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${GOOGLE_CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&response_type=code&scope=openid%20email%20profile`;
    window.location.href = url;
  });

  // Sticky nav shadow on scroll
  const nav = document.getElementById('site-nav');
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 8);
  }, { passive: true });

  // Reveal cards/sections on scroll (progressive, respects reduced motion)
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!prefersReduced && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.style.animationPlayState = 'running';
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.15 });
    document.querySelectorAll('.card').forEach(el => {
      el.style.animationPlayState = 'paused';
      io.observe(el);
    });
  }
