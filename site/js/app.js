/**
 * Chaco Researcher Directory — Main application logic
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize language
  I18n.applyToDOM();

  // Language toggle
  const langBtn = document.querySelector('.lang-toggle');
  if (langBtn) {
    langBtn.addEventListener('click', () => {
      I18n.toggle();
      if (typeof renderPage === 'function') renderPage();
    });
  }

  // Mobile nav toggle
  const navToggle = document.querySelector('.nav-toggle');
  const mainNav = document.querySelector('.main-nav');
  if (navToggle && mainNav) {
    navToggle.addEventListener('click', () => {
      mainNav.classList.toggle('open');
    });
  }
});

/* ===== Shared rendering helpers ===== */

function createResearcherCard(r) {
  const card = document.createElement('a');
  card.className = 'researcher-card';
  card.href = 'profile.html?id=' + encodeURIComponent(r.id);

  // Show broad themes on cards (compact), not keywords
  const themes = (r.themes && r.themes.length > 0)
    ? r.themes.slice(0, 3)
    : (r.thematic_focus.length > 0 ? r.thematic_focus : r.tags_from_seed).slice(0, 3);

  card.innerHTML = `
    <h3>${escapeHtml(r.name)}</h3>
    <div class="affiliation">${escapeHtml(r.affiliation || 'Affiliation pending')}</div>
    <div class="tags">
      ${themes.map(t => `<span class="tag">${escapeHtml(I18n.tTheme(t))}</span>`).join('')}
    </div>
  `;
  return card;
}

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Admin email for the mailto: submission form.
 * Change this to the administrator's email.
 */
const ADMIN_EMAIL = 'yann.lepolaindewaroux@mcgill.ca';
