// CARTO basemap tiles. The key is domain-restricted to m3events.gg in the CARTO dashboard.
const CARTO_TILES = 'https://basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png?key=cb1_4rrh_3_04fa45a35102c24cc7235b9e';

// ── GU36 course map ──
let gu36MapInitialised = false;

function initGU36Map() {
  if (gu36MapInitialised) return;
  const mapEl = document.getElementById('gu36-map');
  if (!mapEl || typeof L === 'undefined') return;
  gu36MapInitialised = true;

  const map = L.map('gu36-map', { zoomControl: true, scrollWheelZoom: false });

  L.tileLayer(CARTO_TILES, {
    attribution: '© OpenStreetMap © CARTO',
    maxZoom: 17
  }).addTo(map);

  new L.GPX('/gpx/GU36_Trail_Race.gpx', {
    async: true,
    marker_options: { startIconUrl: '', endIconUrl: '', shadowUrl: '' },
    polyline_options: {
      color: '#d97706',
      weight: 4,
      opacity: 0.85
    }
  }).on('loaded', function(e) {
    map.fitBounds(e.target.getBounds(), { padding: [20, 20] });
  }).addTo(map);
}
// ── DDO map ──
let ddoMapInitialised = false;

function initDDOMap() {
  if (ddoMapInitialised) return;
  const mapEl = document.getElementById('ddo-map');
  if (!mapEl || typeof L === 'undefined') return;
  ddoMapInitialised = true;
  const map = L.map('ddo-map', { zoomControl: true, scrollWheelZoom: false });
  L.tileLayer(CARTO_TILES, {
    attribution: '© OpenStreetMap © CARTO',
    maxZoom: 17
  }).addTo(map);
  new L.GPX('/gpx/DDO.gpx', {
    async: true,
    marker_options: { startIconUrl: '', endIconUrl: '', shadowUrl: '' },
    polyline_options: { color: '#7c3aed', weight: 4, opacity: 0.85 }
  }).on('loaded', function(e) {
    map.fitBounds(e.target.getBounds(), { padding: [20, 20] });
  }).addTo(map);
}

function showTab(id, event) {
  document.querySelectorAll('.manual-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.manual-tab').forEach(t => t.classList.remove('active'));
  const panel = document.getElementById('tab-' + id);
  if (panel) panel.classList.add('active');
  event.target.classList.add('active');
}

document.addEventListener('DOMContentLoaded', function() {

  // ── Maps (only run where the map element exists) ──
  initDDOMap();
  initGU36Map();

  // ── Event cards: whole card clickable, real link inside for crawlers ──
  document.querySelectorAll('.event-card[data-href]').forEach(function(card) {
    card.addEventListener('click', function(e) {
      if (e.target.closest('a')) return;
      window.location.href = card.getAttribute('data-href');
    });
  });

  // ── Mobile nav dropdown ──
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(function(item) {
    const link = item.querySelector('a');
    const dropdown = item.querySelector('.nav-dropdown');
    if (!dropdown) return;
    link.addEventListener('click', function(e) {
      const isMobile = window.matchMedia('(hover: none)').matches;
      if (!isMobile) return;
      e.preventDefault();
      const isOpen = item.classList.contains('open');
      navItems.forEach(i => i.classList.remove('open'));
      if (!isOpen) item.classList.add('open');
    });
  });
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.nav-item')) {
      navItems.forEach(i => i.classList.remove('open'));
    }
  });

  // ── Mailing list signup ──
  const signupForm = document.getElementById('signup-form');
  if (signupForm) {
    signupForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const btn = document.getElementById('signup-btn');
      const email = document.getElementById('signup-email').value;
      const successMsg = document.getElementById('signup-success');
      const errorMsg = document.getElementById('signup-error');
      btn.textContent = 'Sending…';
      btn.disabled = true;
      successMsg.style.display = 'none';
      errorMsg.style.display = 'none';
      const data = { email: email, subscribed_at: new Date().toLocaleString('en-GB') };
      fetch('https://hooks.zapier.com/hooks/catch/18013361/uvx5e19/', {
        method: 'POST', mode: 'no-cors',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      .then(function() {
        successMsg.style.display = 'block';
        signupForm.reset();
        btn.textContent = 'Signed up ✓';
      })
      .catch(function() {
        errorMsg.style.display = 'block';
        btn.textContent = 'Sign up';
        btn.disabled = false;
      });
    });
  }

  // ── Contact form ──
  const contactForm = document.getElementById('contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const btn = document.getElementById('contact-submit');
      const successMsg = document.getElementById('contact-success');
      const errorMsg = document.getElementById('contact-error');
      btn.textContent = 'Sending…';
      btn.disabled = true;
      successMsg.style.display = 'none';
      errorMsg.style.display = 'none';
      const data = {
        name:         document.querySelector('[name="contact_name"]').value,
        email:        document.querySelector('[name="contact_email"]').value,
        message:      document.querySelector('[name="contact_message"]').value,
        submitted_at: new Date().toLocaleString('en-GB')
      };
      fetch('https://hooks.zapier.com/hooks/catch/18013361/4y18uxk/', {
        method: 'POST',
        mode: 'no-cors',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      .then(function() {
        successMsg.style.display = 'block';
        contactForm.reset();
        btn.textContent = 'Sent ✓';
      })
      .catch(function() {
        errorMsg.style.display = 'block';
        btn.textContent = 'Send message';
        btn.disabled = false;
      });
    });
  }

  // ── Volunteer form ──
  const form = document.getElementById('volunteer-form');
  if (!form) return;
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    const btn = document.getElementById('vol-submit');
    const successMsg = document.getElementById('vol-success');
    const errorMsg = document.getElementById('vol-error');
    btn.textContent = 'Sending…';
    btn.disabled = true;
    successMsg.style.display = 'none';
    errorMsg.style.display = 'none';
    const events = [];
    if (document.getElementById('ev-ddo').checked)  events.push('Donkey Drop Out – Aug 2027');
    if (document.getElementById('ev-gu36').checked) events.push('GU36 – 16 May 2027');
    if (document.getElementById('ev-any').checked)  events.push('Any / all future events');
    const roles = [];
    if (document.getElementById('role-any').checked)     roles.push('No preference');
    if (document.getElementById('role-aid').checked)     roles.push('Aid station crew');
    if (document.getElementById('role-start').checked)   roles.push('Start / finish team');
    if (document.getElementById('role-marshal').checked) roles.push('Course marshal');
    if (document.getElementById('role-sweeper').checked) roles.push('Course sweeper');
    const data = {
      first_name:        document.querySelector('[name="first_name"]').value,
      last_name:         document.querySelector('[name="last_name"]').value,
      email:             document.querySelector('[name="email"]').value,
      phone:             document.querySelector('[name="phone"]').value,
      events:            events.join(', ') || 'None selected',
      roles:             roles.join(', ') || 'None selected',
      other_info:        document.querySelector('[name="other_info"]').value,
      consent_comms:     document.getElementById('consent1').checked ? 'Yes' : 'No',
      consent_marketing: document.getElementById('consent2').checked ? 'Yes' : 'No',
      submitted_at:      new Date().toLocaleString('en-GB')
    };
    fetch('https://hooks.zapier.com/hooks/catch/18013361/uvx2ivu/', {
      method: 'POST', mode: 'no-cors',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    .then(function() {
      successMsg.style.display = 'block';
      form.reset();
      btn.textContent = 'Submitted ✓';
    })
    .catch(function() {
      errorMsg.style.display = 'block';
      btn.textContent = 'Submit volunteer form';
      btn.disabled = false;
    });
  });

}); // end DOMContentLoaded
