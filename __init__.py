# DrugTabs
# Auto-generated DrugTabs cloze add-on

from aqt import mw, gui_hooks

NOTE_TYPE_NAME = "DrugTabs"

FRONT_TEMPLATE = """<div style="display:none">
  {{cloze:Indications}}{{cloze:Contraindications}}{{cloze:Mechanism of Action}}{{cloze:Dosage}}{{cloze:Side Effects}}
  {{cloze:Active Substances}}
</div>

<div class="title">{{Drug}}</div>

<div class="tabs">
  <div class="tab-buttons">
    {{#Indications}}<div class="tab-btn" data-tab="bak">Indications</div>{{/Indications}}
		{{#Contraindications}}<div class="tab-btn" data-tab="kontra">Contraindications</div>{{/Contraindications}}
    {{#Mechanism of Action}}<div class="tab-btn" data-tab="eti">Mechanism of Action</div>{{/Mechanism of Action}}
    {{#Active Substances}}<div class="tab-btn" data-tab="risk">Active Substances</div>{{/Active Substances}}
    {{#Dosage}}<div class="tab-btn" data-tab="pat">Dosage</div>{{/Dosage}}
    {{#Side Effects}}<div class="tab-btn" data-tab="epi">Side Effects</div>{{/Side Effects}}
  </div>

  {{#Indications}}
  <div id="tab-bak" class="tab-panel"><div class="panel-content">
    <div class="content-cloze">{{cloze:Indications}}</div>
    <div class="content-raw" style="display:none">{{Indications}}</div>
  </div></div>
  {{/Indications}}


  {{#Contraindications}}
  <div id="tab-kontra" class="tab-panel"><div class="panel-content">
    <div class="content-cloze">{{cloze:Contraindications}}</div>
    <div class="content-raw" style="display:none">{{Contraindications}}</div>
  </div></div>
  {{/Contraindications}}

  {{#Mechanism of Action}}
  <div id="tab-eti" class="tab-panel"><div class="panel-content">
    <div class="content-cloze">{{cloze:Mechanism of Action}}</div>
    <div class="content-raw" style="display:none">{{Mechanism of Action}}</div>
  </div></div>
  {{/Mechanism of Action}}

  {{#Active Substances}}
  <div id="tab-risk" class="tab-panel"><div class="panel-content">
    <div class="content-cloze">{{cloze:Active Substances}}</div>
    <div class="content-raw" style="display:none">{{Active Substances}}</div>
  </div></div>
  {{/Active Substances}}

  {{#Dosage}}
  <div id="tab-pat" class="tab-panel"><div class="panel-content">
    <div class="content-cloze">{{cloze:Dosage}}</div>
    <div class="content-raw" style="display:none">{{Dosage}}</div>
  </div></div>
  {{/Dosage}}

  {{#Side Effects}}
  <div id="tab-epi" class="tab-panel"><div class="panel-content">
    <div class="content-cloze">{{cloze:Side Effects}}</div>
    <div class="content-raw" style="display:none">{{Side Effects}}</div>
  </div></div>
  {{/Side Effects}}

</div>

<script>
(function () {
  // Hjälpare
  const $  = s => document.querySelector(s);
  const $$ = s => Array.from(document.querySelectorAll(s));

  // Undvik att trigga Ankis parser
  const OPEN  = String.fromCharCode(123,123);
  const CLOSE = String.fromCharCode(125,125);
  const reCloze = new RegExp(OPEN + 'c\\\\d+::' + '([\\\\s\\\\S]*?)' + '(?:::[^}]+)?' + CLOSE, 'g');

  function stripClozeFromHTML(html) {
    return (html || '').replace(reCloze, '$1');
  }

  // Rendera panelinnehåll beroende på läge
  function renderPanel(panelEl, mode) {
    const cont    = panelEl.querySelector('.panel-content');
    const clozeEl = cont && cont.querySelector('.content-cloze');
    const rawEl   = cont && cont.querySelector('.content-raw');
    if (!cont || !clozeEl || !rawEl) return;

    const clozeHTML = (clozeEl.innerHTML || '').trim();
    const rawHTML   = rawEl.innerHTML || '';

    if (mode === 'question') {
      cont.innerHTML = clozeHTML ? clozeHTML : stripClozeFromHTML(rawHTML);
    } else {
      cont.innerHTML = stripClozeFromHTML(rawHTML);
    }
  }

  // --- Autoscroll till aktiv flik (mobil) ---
  const isMobile = () => window.matchMedia('(max-width: 640px)').matches;

  function ensureActiveTabVisible(smooth) {
    if (!isMobile()) return;
    const container = $('.tab-buttons');
    if (!container) return;

    const active = container.querySelector('.tab-btn.active') || container.querySelector('.tab-btn');
    if (!active) return;

    const cRect = container.getBoundingClientRect();
    const aRect = active.getBoundingClientRect();

    let delta = 0;
    if (aRect.left < cRect.left) {
      delta = aRect.left - cRect.left;   // scrolla vänster
    } else if (aRect.right > cRect.right) {
      delta = aRect.right - cRect.right; // scrolla höger
    }
    if (delta !== 0) {
      container.scrollTo({ left: container.scrollLeft + delta, behavior: smooth ? 'smooth' : 'auto' });
    }
  }

  // Kör efter layout (dubbla rAF = stabilt även när webview återanvänds)
  function queueEnsure(smooth) {
    requestAnimationFrame(() => requestAnimationFrame(() => ensureActiveTabVisible(smooth)));
  }

  // --- Init ---
  const panelObjs = $$('.tab-panel').map(el => ({ id: el.id.replace('tab-',''), el }));
  const btns      = $$('.tab-btn');

  // Välj startflik: första med cloze-innehåll, annars första
  let activeId = panelObjs.length ? panelObjs[0].id : '';
  for (const p of panelObjs) {
    const c = p.el.querySelector('.content-cloze');
    if (c && (c.innerHTML || '').trim()) { activeId = p.id; break; }
  }

  function rerenderAll() {
    panelObjs.forEach(p => {
      renderPanel(p.el, p.id === activeId ? 'question' : 'plain');
      p.el.classList.toggle('active', p.id === activeId);
    });
    btns.forEach(b => b.classList.toggle('active', b.dataset.tab === activeId));
    queueEnsure(false);
  }

  rerenderAll();

  // Klick: byt flik
  btns.forEach(b => b.addEventListener('click', () => {
    activeId = b.dataset.tab;
    rerenderAll();
    queueEnsure(true);
  }));

  // Space/Enter på framsidan -> vänd kort
  document.addEventListener('keydown', function(e){
    const k = e.key || e.code;
    const isSpace = k === ' ' || k === 'Spacebar' || k === 'Space';
    const isEnter = k === 'Enter';
    const onBack  = !!document.getElementById('answer');
    const tag     = (document.activeElement && document.activeElement.tagName) || '';
    if (!onBack && (isSpace || isEnter) &&
        !/^(INPUT|TEXTAREA|SELECT)$/.test(tag) &&
        typeof pycmd === 'function') {
      e.preventDefault();
      pycmd('ans');
    }
  }, {passive:false});

  // Håll autoscroll vid liv i Anki (återanvänd webview, rotation, osv.)
  queueEnsure(false);
  window.addEventListener('resize', () => queueEnsure(false));
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') queueEnsure(false);
  });

  // Om något ändrar klasser i knappraden (t.ex. via andra skript), justera scroll
  const container = document.querySelector('.tab-buttons');
  if (container && 'MutationObserver' in window) {
    const mo = new MutationObserver(() => queueEnsure(false));
    mo.observe(container, {subtree: true, childList: true, attributes: true, attributeFilter: ['class']});
  }
})();
</script>
"""

BACK_TEMPLATE = """<div style="display:none">
  {{cloze:Indications}}{{cloze:Mechanism of Action}}{{cloze:Dosage}}{{cloze:Side Effects}}
  {{cloze:Active Substances}}
</div>

<div class="title">{{Drug}}</div>

<div class="tabs">
  <div class="tab-buttons">
    {{#Indications}}<div class="tab-btn" data-tab="bak">Indikationer</div>{{/Indications}}
		{{#Contraindications}}<div class="tab-btn" data-tab="kontra">Kontraindikationer</div>{{/Contraindications}}
    {{#Mechanism of Action}}<div class="tab-btn" data-tab="eti">Verkningsmekanism</div>{{/Mechanism of Action}}
    {{#Active Substances}}<div class="tab-btn" data-tab="risk">Preparat</div>{{/Active Substances}}
    {{#Dosage}}<div class="tab-btn" data-tab="pat">Dosering</div>{{/Dosage}}
    {{#Side Effects}}<div class="tab-btn" data-tab="epi">Biverkningar</div>{{/Side Effects}}
  </div>

  {{#Indications}}
  <div id="tab-bak" class="tab-panel"><div class="panel-content">
    <div class="content-cloze">{{cloze:Indications}}</div>
    <div class="content-raw" style="display:none">{{Indications}}</div>
  </div></div>
  {{/Indications}}


  {{#Contraindications}}
  <div id="tab-kontra" class="tab-panel"><div class="panel-content">
    <div class="content-cloze">{{cloze:Contraindications}}</div>
    <div class="content-raw" style="display:none">{{Contraindications}}</div>
  </div></div>
  {{/Contraindications}}

  {{#Mechanism of Action}}
  <div id="tab-eti" class="tab-panel"><div class="panel-content">
    <div class="content-cloze">{{cloze:Mechanism of Action}}</div>
    <div class="content-raw" style="display:none">{{Mechanism of Action}}</div>
  </div></div>
  {{/Mechanism of Action}}

  {{#Active Substances}}
  <div id="tab-risk" class="tab-panel"><div class="panel-content">
    <div class="content-cloze">{{cloze:Active Substances}}</div>
    <div class="content-raw" style="display:none">{{Active Substances}}</div>
  </div></div>
  {{/Active Substances}}

  {{#Dosage}}
  <div id="tab-pat" class="tab-panel"><div class="panel-content">
    <div class="content-cloze">{{cloze:Dosage}}</div>
    <div class="content-raw" style="display:none">{{Dosage}}</div>
  </div></div>
  {{/Dosage}}

  {{#Side Effects}}
  <div id="tab-epi" class="tab-panel"><div class="panel-content">
    <div class="content-cloze">{{cloze:Side Effects}}</div>
    <div class="content-raw" style="display:none">{{Side Effects}}</div>
  </div></div>
  {{/Side Effects}}

</div>
<div class="panel-extra">{{Extra}}</div>

<script>
(function () {
  const $  = s => document.querySelector(s);
  const $$ = s => Array.from(document.querySelectorAll(s));

  // Bygg via charCode för att inte trigga Ankis parser
  const OPEN  = String.fromCharCode(123,123);
  const CLOSE = String.fromCharCode(125,125);
  const reCloze = new RegExp(OPEN + 'c\\\\d+::' + '([\\\\s\\\\S]*?)' + '(?:::[^}]+)?' + CLOSE, 'g');

  function stripClozeFromHTML(html) {
    if (!html) return '';
    return html.replace(reCloze, '$1');
  }

  // På baksidan: visa cloze om den finns, annars ren text utan cloze-taggar
  function ensurePanelHasContent(panelEl){
    if (!panelEl) return;
    const cont    = panelEl.querySelector('.panel-content');
    const clozeEl = cont && cont.querySelector('.content-cloze');
    const rawEl   = cont && cont.querySelector('.content-raw');

    const clozeHTML = (clozeEl && clozeEl.innerHTML) ? clozeEl.innerHTML.trim() : '';
    const rawHTML   = rawEl ? (rawEl.innerHTML || '') : '';

    if (clozeHTML) {
      if (rawEl) rawEl.remove();
      cont.innerHTML = clozeHTML;
    } else {
      cont.innerHTML = stripClozeFromHTML(rawHTML);
    }
  }

  const panels = $$('.tab-panel');
  const btns   = $$('.tab-btn');

  // Förbered panelerna
  panels.forEach(el => ensurePanelHasContent(el));

  function openTab(id){
    panels.forEach(p => p.classList.toggle('active', p.id === 'tab-' + id));
    btns.forEach(b => b.classList.toggle('active', b.dataset.tab === id));
  }

  // Startflik = första panel som har .cloze, annars första panel
  let startId = '';
  for (const p of panels) {
    if (p.querySelector('.panel-content .cloze')) { startId = p.id.replace('tab-',''); break; }
  }
  if (!startId && panels.length) startId = panels[0].id.replace('tab-','');
  if (startId) openTab(startId);

  // Byt flik via klick
  btns.forEach(b => b.addEventListener('click', () => openTab(b.dataset.tab)));

  // --- Autoscroll: se till att aktiv flik syns på mobil ---
  const isMobile = () => window.matchMedia('(max-width: 640px)').matches;

  function ensureActiveTabVisible(smooth) {
    if (!isMobile()) return;
    const container = document.querySelector('.tab-buttons');
    if (!container) return;
    const active = container.querySelector('.tab-btn.active') || container.querySelector('.tab-btn');
    if (!active) return;

    const cRect = container.getBoundingClientRect();
    const aRect = active.getBoundingClientRect();

    let delta = 0;
    if (aRect.left < cRect.left)      delta = aRect.left - cRect.left;   // scrolla vänster
    else if (aRect.right > cRect.right) delta = aRect.right - cRect.right; // scrolla höger

    if (delta !== 0) {
      container.scrollTo({
        left: container.scrollLeft + delta,
        behavior: smooth ? 'smooth' : 'auto'
      });
    }
  }

  // Kör efter layouten satt sig (dubbel rAF hjälper i Ankis webview)
  function queueEnsure(smooth){
    requestAnimationFrame(() => {
      requestAnimationFrame(() => ensureActiveTabVisible(smooth));
    });
  }

  // Init
  queueEnsure(false);

  // Säkerställ vid resize/rotation
  window.addEventListener('resize', () => queueEnsure(false));

  // När kortet blir synligt igen i återanvänd webview
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') queueEnsure(false);
  });

  // Efter flikbyte
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.tab-btn');
    if (!btn) return;
    setTimeout(() => queueEnsure(true), 0);
  });

  // Om Anki manipulerar DOM-klasser, re-scrolla
  const container = document.querySelector('.tab-buttons');
  if (container && 'MutationObserver' in window) {
    const mo = new MutationObserver(() => queueEnsure(false));
    mo.observe(container, {subtree: true, childList: true, attributes: true, attributeFilter: ['class']});
  }
})();
</script>


<br><br>
<div id="bildkälla" style="font-size: 7px; color: gray;">
  
</div>

"""

CSS = """.card { 
  font-family: -apple-system, Inter, Segoe UI, Roboto, sans-serif; 
  font-size: 18px; 
  line-height: 1.45; 
  max-width: 55rem; 
  margin: 0 auto; 
  background: #ffffff;
  color: #000000; /* svart text */
}

/* Titel */
.title {
  font-size: 24px;
  font-weight: 700;
  text-align: center;
  margin: 20px 0;
  color: var(--fg);
}

/* Flikcontainer */
.tabs { 
  border: 1px solid #7ea17e;        /* grönt motsv. #a8a8a8 */
  border-radius: 10px;
  overflow: hidden;
  background: #b8d0b8;              /* ljusare containergrön (~#dcdcdc) */
}

/* Flikknappar + scrollbar */
.tab-buttons { 
  display: flex;
  border-bottom: 1px solid #7ea17e; 
  background: #a9c4a9;              
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
}

.tab-buttons::-webkit-scrollbar { height: 6px; }
.tab-buttons::-webkit-scrollbar-thumb { 
  background: rgba(0,0,0,0.15); 
  border-radius: 4px; 
}
.tab-buttons::-webkit-scrollbar-track { background: transparent; }

/* Tabbar */
.tab-btn { 
  flex: 1;
  padding: 6px 8px;            
  font-size: 14px;             
  font-weight: 500;            
  border: 0; 
  background: transparent; 
  color: #2f402f;                 /* mörkare grön/grå text */
  cursor: pointer; 
  transition: background .15s ease, color .15s ease; 
  user-select: none; 
}

/* Mobil */
@media (max-width: 640px) {
  .tab-buttons {
    width: 100%;
  }
  .tab-btn {
    flex: 1 0 auto;
    padding: 6px 12px;
    font-size: 11px;
    scroll-snap-align: start;
  }
}

/* Hover */
.tab-btn:hover { 
  background: #97b897;            /* grön motsv. #bdbdbd */
  color: #1d291d; 
}

/* Aktiv flik */
.tab-btn.active { 
  background: #89ad89;            /* grön motsv. #b0b0b0 */
  color: #0f190f; 
}

/* Paneler */
.tab-panel { 
  display: none; 
  padding: 10px 12px; 
  background: #cbe0cb;            /* grön motsv. #e6e6e6 */
  color: #000;                   
  font-size: 16px;
  line-height: 1.45;
}

.tab-panel.active { display: block; }

/* Panelinnehåll */
.panel-content { 
  white-space: pre-wrap; 
  word-wrap: break-word; 
}

/* Cloze-text – mörk Anki-blå */
.cloze { 
  font-weight: bold; 
  text-decoration: none !important;
  color: #0B3FD4 !important;
}

/* Cloze på baksidan */
#answer ~ .tabs .cloze {
  font-weight: bold;
  text-decoration: none !important;
  color: #0B3FD4 !important;
}

/* Extra-fält */
.panel-extra {
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  font-style: italic;
  color: #888;
  text-align: center;
  display: block;
  width: 100%;
  line-height: 1.2;
}

/* Hint */
.hint { 
  font-size: 7px; 
  color: gray !important; 
  text-align: center;
  display: block;
  margin-top: 0.3em;
}

/* Hint inline */
.hint[style*="display: inline;"] { 
  color: black !important;
  display: inline;
  text-align: left;
}
"""

FIELDS = ["Drug", "Indications", "Contraindications", "Mechanism of Action", "Active Substances", "Dosage", "Side Effects", "Extra"]


def create_note_type():
    col = mw.col
    existing = col.models.by_name(NOTE_TYPE_NAME)
    if existing:
        return

    m = col.models.new(NOTE_TYPE_NAME)
    m["type"] = 1  # cloze type

    for field_name in FIELDS:
        fld = col.models.new_field(field_name)
        col.models.add_field(m, fld)

    t = col.models.new_template("DrugTabs Card")
    t["qfmt"] = FRONT_TEMPLATE
    t["afmt"] = BACK_TEMPLATE
    col.models.add_template(m, t)

    m["css"] = CSS
    col.models.add(m)
    col.models.save(m)


def on_profile_loaded():
    create_note_type()


gui_hooks.profile_did_open.append(on_profile_loaded)
