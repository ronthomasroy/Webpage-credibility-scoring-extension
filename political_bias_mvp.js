<<<<<<< HEAD
(() => {
  // --- CONFIG: entities ---
  const entities = [
    'party a','party b','hiemer','john',
    'pa','pb',
    'trump','biden',
    'democrat','democrats',
    'republican','republicans'
  ];

  // --- 1. NER-style counts (console output) ---
  (function countEntities() {
    const t = document.body.innerText.toLowerCase();
    const counts = {};
    entities.forEach(name => {
      // word-boundary-ish regex (handles spaces in names too)
      const pattern = '\\b' + name.replace(/\s+/g, '\\s+') + '\\b';
      const match = t.match(new RegExp(pattern, 'g')) || [];
      counts[name] = match.length;
    });
    console.table(counts);
  })();

  // --- 2. Extract main page text for bias calc ---
  function getBodyText() {
    return [...document.querySelectorAll('p, div, article, main')]
      .map(n => n.innerText)
      .join(' ')
      .replace(/\s+/g, ' ')
      .slice(0, 8000);
  }

  // --- 3. Tiny sentiment lexicon ---
  function sentiment(w) {
    const neg = ['bad','worst','failed','corrupt','lies','attack','hate','fraud','scam','evil','dirty',
    'criticised','criticism','blamed','condemned','accused','scandal','controversy','violent','target'];
    const pos = ['good','best','progress','clean','honest','boost','reform','success','development','growth',
    'praised','hailed','lauded','support','supported','backed','welcomed','improved'];
    w = w.toLowerCase();
    if (neg.includes(w)) return -1;
    if (pos.includes(w)) return 1;
    return 0;
  }

  // --- 4. microTSEA (stance–emotion asymmetry) ---
  function microTSEA(text) {
    const sents = text
      .split(/[.!?]+/)
      .map(s => s.trim())
      .filter(s => s.length > 10);

    const map = {};
    entities.forEach(e => {
      map[e] = { stance: 0, cnt: 0, emo: 0 };
    });

    sents.forEach(st => {
      const lower = st.toLowerCase();
      entities.forEach(e => {
        if (lower.includes(e)) {
          let stance = 0, emo = 0, hits = 0;
          st.split(/\W+/).forEach(w => {
            const s = sentiment(w);
            if (s !== 0) {
              stance += s;
              emo    += Math.abs(s);
              hits++;
            }
          });
          if (hits) {
            map[e].stance += stance / hits;
            map[e].emo    += emo / hits;
            map[e].cnt    += 1;
          }
        }
      });
    });

    const filt = Object.entries(map).filter(([, v]) => v.cnt >= 1);
    if (filt.length < 2) return 0;

    const sc = filt.map(([, v]) => {
      const meanStance = v.stance / v.cnt;
      const meanEmo    = v.emo / v.cnt;
      return meanStance * meanEmo || 0;
    });

    const avg  = sc.reduce((a, b) => a + b, 0) / sc.length;
    const vari = sc.reduce((a, b) => a + Math.pow(b - avg, 2), 0) / sc.length;
    return Math.sqrt(vari);
  }

  // --- 5. Run and show bias bar ---
  const text = getBodyText();
  const rawScore = microTSEA(text);
  const score = Math.max(0, Math.min(rawScore * 100, 100));

  const old = document.getElementById('tsea-bias-bar');
  if (old) old.remove();

  const bar = document.createElement('div');
  bar.id = 'tsea-bias-bar';
  bar.style = `
    position:fixed;
    bottom:10px;
    left:10px;
    width:260px;
    background:#111;
    color:#fff;
    padding:8px 10px;
    border-radius:6px;
    z-index:999999;
    font:13px/1.4 system-ui, sans-serif;
    box-shadow:0 2px 6px rgba(0,0,0,0.4);
  `;
const biasScore = 100 - score;          // invert
bar.innerHTML = `
    <div style="font-weight:600;margin-bottom:4px;">political_bias_score (mvp)</div><small>(100 = balanced, 0 = very biased)</small>
    <div style="font-size:18px;color:#f9c74f;margin-bottom:2px;">
      ${biasScore.toFixed(0)}/100
    </div>
  `;
  document.body.appendChild(bar);
})();
=======
(() => {
  // --- CONFIG: entities ---
  const entities = [
    'party a','party b','hiemer','john',
    'pa','pb',
    'trump','biden',
    'democrat','democrats',
    'republican','republicans'
  ];

  // --- 1. NER-style counts (console output) ---
  (function countEntities() {
    const t = document.body.innerText.toLowerCase();
    const counts = {};
    entities.forEach(name => {
      // word-boundary-ish regex (handles spaces in names too)
      const pattern = '\\b' + name.replace(/\s+/g, '\\s+') + '\\b';
      const match = t.match(new RegExp(pattern, 'g')) || [];
      counts[name] = match.length;
    });
    console.table(counts);
  })();

  // --- 2. Extract main page text for bias calc ---
  function getBodyText() {
    return [...document.querySelectorAll('p, div, article, main')]
      .map(n => n.innerText)
      .join(' ')
      .replace(/\s+/g, ' ')
      .slice(0, 8000);
  }

  // --- 3. Tiny sentiment lexicon ---
  function sentiment(w) {
    const neg = ['bad','worst','failed','corrupt','lies','attack','hate','fraud','scam','evil','dirty',
    'criticised','criticism','blamed','condemned','accused','scandal','controversy','violent','target'];
    const pos = ['good','best','progress','clean','honest','boost','reform','success','development','growth',
    'praised','hailed','lauded','support','supported','backed','welcomed','improved'];
    w = w.toLowerCase();
    if (neg.includes(w)) return -1;
    if (pos.includes(w)) return 1;
    return 0;
  }

  // --- 4. microTSEA (stance–emotion asymmetry) ---
  function microTSEA(text) {
    const sents = text
      .split(/[.!?]+/)
      .map(s => s.trim())
      .filter(s => s.length > 10);

    const map = {};
    entities.forEach(e => {
      map[e] = { stance: 0, cnt: 0, emo: 0 };
    });

    sents.forEach(st => {
      const lower = st.toLowerCase();
      entities.forEach(e => {
        if (lower.includes(e)) {
          let stance = 0, emo = 0, hits = 0;
          st.split(/\W+/).forEach(w => {
            const s = sentiment(w);
            if (s !== 0) {
              stance += s;
              emo    += Math.abs(s);
              hits++;
            }
          });
          if (hits) {
            map[e].stance += stance / hits;
            map[e].emo    += emo / hits;
            map[e].cnt    += 1;
          }
        }
      });
    });

    const filt = Object.entries(map).filter(([, v]) => v.cnt >= 1);
    if (filt.length < 2) return 0;

    const sc = filt.map(([, v]) => {
      const meanStance = v.stance / v.cnt;
      const meanEmo    = v.emo / v.cnt;
      return meanStance * meanEmo || 0;
    });

    const avg  = sc.reduce((a, b) => a + b, 0) / sc.length;
    const vari = sc.reduce((a, b) => a + Math.pow(b - avg, 2), 0) / sc.length;
    return Math.sqrt(vari);
  }

  // --- 5. Run and show bias bar ---
  const text = getBodyText();
  const rawScore = microTSEA(text);
  const score = Math.max(0, Math.min(rawScore * 100, 100));

  const old = document.getElementById('tsea-bias-bar');
  if (old) old.remove();

  const bar = document.createElement('div');
  bar.id = 'tsea-bias-bar';
  bar.style = `
    position:fixed;
    bottom:10px;
    left:10px;
    width:260px;
    background:#111;
    color:#fff;
    padding:8px 10px;
    border-radius:6px;
    z-index:999999;
    font:13px/1.4 system-ui, sans-serif;
    box-shadow:0 2px 6px rgba(0,0,0,0.4);
  `;
const biasScore = 100 - score;          // invert
bar.innerHTML = `
    <div style="font-weight:600;margin-bottom:4px;">political_bias_score (mvp)</div><small>(100 = balanced, 0 = very biased)</small>
    <div style="font-size:18px;color:#f9c74f;margin-bottom:2px;">
      ${biasScore.toFixed(0)}/100
    </div>
  `;
  document.body.appendChild(bar);
})();
>>>>>>> d57ef291d69b934d3a0154eee29a159c4c9a7e3f
