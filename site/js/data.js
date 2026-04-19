/**
 * Chaco Researcher Directory — Data loading and management
 */

const ChacoData = (() => {
  let _researchers = null;
  let _normalizedNameIndex = null;
  let _surnameFirstIndex = null;
  let _surnameIndex = null;

  function normalizeText(value) {
    return (value || '')
      .toString()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase();
  }

  function normalizePersonReference(value) {
    return normalizeText(value)
      .replace(/-/g, ' ')
      .replace(/[^a-z0-9, ]+/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  function buildReferenceIndexes() {
    if (_normalizedNameIndex && _surnameFirstIndex && _surnameIndex) return;
    _normalizedNameIndex = new Map();
    _surnameFirstIndex = new Map();
    _surnameIndex = new Map();

    (_researchers || []).forEach(researcher => {
      const normalized = normalizePersonReference(researcher.name);
      if (normalized) {
        _normalizedNameIndex.set(normalized, researcher);
      }

      const key = getSurnameFirstKey(researcher.name);
      if (!key) return;
      const existing = _surnameFirstIndex.get(key) || [];
      existing.push(researcher);
      _surnameFirstIndex.set(key, existing);

      const parsed = parsePersonReference(researcher.name);
      if (parsed && parsed.surname) {
        const surnameMatches = _surnameIndex.get(parsed.surname) || [];
        surnameMatches.push(researcher);
        _surnameIndex.set(parsed.surname, surnameMatches);
      }
    });
  }

  function getSurnameFirstKey(value) {
    const parsed = parsePersonReference(value);
    if (!parsed || parsed.givenTokens.length === 0) return null;
    return `${parsed.surname}::${parsed.givenTokens[0]}`;
  }

  function parsePersonReference(value) {
    const normalized = normalizePersonReference(value);
    if (!normalized.includes(',')) return null;
    const parts = normalized.split(',');
    const surname = (parts[0] || '').trim();
    const givenTokens = ((parts[1] || '').trim()).split(' ').filter(Boolean);
    if (!surname) return null;
    return { surname, givenTokens };
  }

  function getCandidateGivenMetadata(name) {
    const parsed = parsePersonReference(name);
    if (!parsed) return null;
    const initials = parsed.givenTokens.map(token => token[0]).join('');
    return {
      surname: parsed.surname,
      givenTokens: parsed.givenTokens,
      initials
    };
  }

  function isInitialToken(token) {
    return token.length <= 2;
  }

  function candidateMatchesReference(candidate, referenceTokens) {
    const meta = getCandidateGivenMetadata(candidate.name);
    if (!meta) return false;

    return referenceTokens.every(token => {
      if (isInitialToken(token)) {
        return meta.initials.startsWith(token) || meta.givenTokens.some(given => given.startsWith(token));
      }
      return meta.givenTokens.includes(token);
    });
  }

  async function load() {
    if (_researchers) return _researchers;
    const basePath = getBasePath();
    const resp = await fetch(basePath + 'data/researchers.json');
    _researchers = await resp.json();
    _normalizedNameIndex = null;
    _surnameFirstIndex = null;
    return _researchers;
  }

  function getBasePath() {
    const path = window.location.pathname;
    if (path.includes('/site/')) {
      return path.substring(0, path.indexOf('/site/') + 6);
    }
    return './';
  }

  function getAll() {
    return _researchers || [];
  }

  function getById(id) {
    if (!_researchers) return null;
    return _researchers.find(r => r.id === id) || null;
  }

  function resolveResearcherRef(reference) {
    if (!_researchers || !reference) return null;

    const exact = _researchers.find(r => r.id === reference || r.name === reference);
    if (exact) return exact;

    buildReferenceIndexes();

    const normalized = normalizePersonReference(reference);
    if (!normalized) return null;

    const normalizedMatch = _normalizedNameIndex.get(normalized);
    if (normalizedMatch) return normalizedMatch;

    const key = getSurnameFirstKey(reference);
    if (!key) return null;

    const candidates = _surnameFirstIndex.get(key) || [];
    if (candidates.length === 1) return candidates[0];

    const parsed = parsePersonReference(reference);
    if (!parsed || parsed.givenTokens.length === 0) return null;

    const surnameCandidates = _surnameIndex.get(parsed.surname) || [];
    const narrowed = surnameCandidates.filter(candidate => candidateMatchesReference(candidate, parsed.givenTokens));
    return narrowed.length === 1 ? narrowed[0] : null;
  }

  /**
   * Get the featured researcher of the day.
   * Uses the date as a seed for deterministic "random" selection.
   */
  function getFeaturedOfDay() {
    if (!_researchers || _researchers.length === 0) return null;
    const today = new Date();
    const daysSinceEpoch = Math.floor(today.getTime() / (1000 * 60 * 60 * 24));
    const index = daysSinceEpoch % _researchers.length;
    return _researchers[index];
  }

  /**
   * Filter researchers by criteria.
   * @param {Object} filters - { search, theme, geoFocus, affiliationCountry }
   */
  function filter(filters) {
    let results = _researchers || [];

    if (filters.search) {
      const q = normalizeText(filters.search);
      results = results.filter(r => {
        return normalizeText(r.name).includes(q)
          || (r.affiliation && normalizeText(r.affiliation).includes(q))
          || (r.research_description_en && normalizeText(r.research_description_en).includes(q))
          || (r.research_description_es && normalizeText(r.research_description_es).includes(q))
          || (r.thematic_focus && r.thematic_focus.some(t => normalizeText(t).includes(q)))
          || (r.geographical_focus && r.geographical_focus.some(g => normalizeText(g).includes(q) || normalizeText(I18n.tGeo(g)).includes(q)))
          || (r.themes && r.themes.some(t => normalizeText(t).includes(q) || normalizeText(I18n.tTheme(t)).includes(q)))
          || (r.keywords && r.keywords.some(k => normalizeText(k).includes(q) || normalizeText(I18n.tKeyword(k)).includes(q)))
          || (r.tags_from_seed && r.tags_from_seed.some(t => normalizeText(t).includes(q)))
          || (r.publications && r.publications.some(p => normalizeText(p.title).includes(q)));
      });
    }

    // Theme filter: matches against the broad "themes" array
    if (filters.theme) {
      const theme = filters.theme;
      results = results.filter(r =>
        r.themes && r.themes.some(t => t === theme)
      );
    }

    // Geographic focus filter: where the researcher's work is located
    if (filters.geoFocus) {
      const geo = normalizeText(filters.geoFocus);
      results = results.filter(r =>
        (r.geographical_focus && r.geographical_focus.some(g => normalizeText(g).includes(geo)))
        || (r.tags_from_seed && r.tags_from_seed.some(t => normalizeText(t) === geo))
        || (r.keywords && r.keywords.some(k => normalizeText(k) === geo))
      );
    }

    // Affiliation country filter: where the researcher is based
    if (filters.affiliationCountry) {
      const ac = normalizeText(filters.affiliationCountry);
      results = results.filter(r =>
        (r.country && normalizeText(r.country).includes(ac))
        || (r.affiliation && normalizeText(r.affiliation).includes(ac))
      );
    }

    return results;
  }

  /**
   * Get all unique broad themes across all researchers.
   */
  function getAllThemes() {
    if (!_researchers) return [];
    const themes = new Set();
    _researchers.forEach(r => {
      if (r.themes) r.themes.forEach(t => themes.add(t));
    });
    return Array.from(themes).sort();
  }

  /**
   * Get all unique keywords across all researchers.
   */
  function getAllKeywords() {
    if (!_researchers) return [];
    const kw = new Set();
    _researchers.forEach(r => {
      if (r.keywords) r.keywords.forEach(k => kw.add(k));
    });
    return Array.from(kw).sort();
  }

  return {
    load,
    getAll,
    getById,
    resolveResearcherRef,
    getFeaturedOfDay,
    filter,
    getAllThemes,
    getAllKeywords,
    normalizeText
  };
})();
