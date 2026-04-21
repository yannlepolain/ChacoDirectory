const ChacoHomeMap = (() => {
  const data = window.ChacoCollabMapData || {};
  const MAP_WIDTH = data.mapWidth || 1000;
  const MAP_HEIGHT = data.mapHeight || 500;
  const MAP_VIEWBOX = `0 0 ${MAP_WIDTH} ${MAP_HEIGHT}`;
  const MAP_ASPECT = MAP_WIDTH / MAP_HEIGHT;

  const A1 = 1.340264;
  const A2 = -0.081106;
  const A3 = 0.000893;
  const A4 = 0.003796;
  const M = Math.sqrt(3) / 2;
  const RAW_X_MAX = 2.7066299836960748;
  const RAW_Y_MAX = 1.3173627591574133;
  const RAW_X_MIN = -RAW_X_MAX;
  const MAP_PADDING_X = 8;
  const MAP_SCALE = (MAP_WIDTH - (MAP_PADDING_X * 2)) / (RAW_X_MAX - RAW_X_MIN);
  const PROJECTED_HEIGHT = (RAW_Y_MAX * 2) * MAP_SCALE;
  const MAP_OFFSET_X = MAP_PADDING_X;
  const MAP_OFFSET_Y = (MAP_HEIGHT - PROJECTED_HEIGHT) / 2;

  const WORLD_COUNTRY_ANCHOR_OVERRIDES = new Set([
    'Belgium',
    'France',
    'Germany',
    'Italy',
    'Netherlands',
    'Norway',
    'Spain',
    'Switzerland',
    'United Kingdom'
  ]);

  const stateByContainer = new WeakMap();

  const AFFILIATION_LOCATION_KEYWORDS = [
    { patterns: ['universidad de buenos aires', 'instituto de ciencias antropologicas', 'cefybo', 'universidad nacional de san martin'], lat: -34.6037, lng: -58.3816, city: 'Buenos Aires', country: 'Argentina' },
    { patterns: ['universidad nacional de cordoba', 'idacor', 'imbiv', 'iibyt', 'cernar', 'centro de zoologia aplicada', 'facultad de ciencias agropecuarias'], lat: -31.4201, lng: -64.1888, city: 'Cordoba', country: 'Argentina' },
    { patterns: ['universidad nacional de tucuman', 'instituto de ecologia regional', 'ier', 'ises', 'inteph', 'iiacs'], lat: -26.8083, lng: -65.2176, city: 'San Miguel de Tucuman', country: 'Argentina' },
    { patterns: ['universidad nacional de santiago del estero', 'indes', 'inta eea santiago del estero'], lat: -27.7834, lng: -64.2642, city: 'Santiago del Estero', country: 'Argentina' },
    { patterns: ['universidad nacional de salta', 'inenco'], lat: -24.7821, lng: -65.4232, city: 'Salta', country: 'Argentina' },
    { patterns: ['icsoh', 'conicet-unsa'], lat: -24.7821, lng: -65.4232, city: 'Salta', country: 'Argentina' },
    { patterns: ['iighi', 'instituto de investigaciones geohistoricas'], lat: -27.4514, lng: -58.9867, city: 'Resistencia', country: 'Argentina' },
    { patterns: ['universidad nacional del nordeste'], lat: -27.4692, lng: -58.8306, city: 'Corrientes', country: 'Argentina' },
    { patterns: ['ishir', 'universidad nacional de rosario'], lat: -32.9442, lng: -60.6505, city: 'Rosario', country: 'Argentina' },
    { patterns: ['universidad nacional del litoral', 'facultad de bioquimica y ciencias biologicas'], lat: -31.6333, lng: -60.7000, city: 'Santa Fe', country: 'Argentina' },
    { patterns: ['universidad nacional del sur'], lat: -38.7196, lng: -62.2724, city: 'Bahia Blanca', country: 'Argentina' },
    { patterns: ['universidad nacional de jujuy', 'inecoa', 'cetas-unju'], lat: -24.1858, lng: -65.2995, city: 'San Salvador de Jujuy', country: 'Argentina' },
    { patterns: ['secretaria de ambiente y desarrollo sustentable', 'direccion de fauna silvestre'], lat: -34.6037, lng: -58.3816, city: 'Buenos Aires', country: 'Argentina' },
    { patterns: ['universidad nacional de la plata', 'lias'], lat: -34.9214, lng: -57.9544, city: 'La Plata', country: 'Argentina' },
    { patterns: ['universidad nacional de quilmes'], lat: -34.7203, lng: -58.2546, city: 'Quilmes', country: 'Argentina' },
    { patterns: ['universidad nacional de misiones', 'instituto de biologia subtropical (ibs)', 'instituto de biologia subtropical'], lat: -27.3621, lng: -55.9009, city: 'Posadas', country: 'Argentina' },
    { patterns: ['universidad nacional de formosa', 'inilsyt'], lat: -26.1849, lng: -58.1731, city: 'Formosa', country: 'Argentina' },
    { patterns: ['universidad nacional arturo jauretche'], lat: -34.7719, lng: -58.2676, city: 'Florencio Varela', country: 'Argentina' },
    { patterns: ['universidad nacional del centro de la provincia de buenos aires', 'uncpba', 'igehcs'], lat: -37.3217, lng: -59.1332, city: 'Tandil', country: 'Argentina' },
    { patterns: ['universidad nacional de san juan', 'irpha'], lat: -31.5375, lng: -68.5364, city: 'San Juan', country: 'Argentina' },
    { patterns: ['ciafic'], lat: -34.6037, lng: -58.3816, city: 'Buenos Aires', country: 'Argentina' },
    { patterns: ['inta estacion experimental agropecuaria santiago del estero'], lat: -27.7951, lng: -64.2615, city: 'Santiago del Estero', country: 'Argentina' },
    { patterns: ['ibigeo'], lat: -24.7821, lng: -65.4232, city: 'Salta', country: 'Argentina' },
    { patterns: ['incitap'], lat: -36.6203, lng: -64.2906, city: 'Santa Rosa', country: 'Argentina' },
    { patterns: ['iidypca', 'universidad nacional de rio negro', 'unrn'], lat: -41.1335, lng: -71.3103, city: 'San Carlos de Bariloche', country: 'Argentina' },
    { patterns: ['universidad nacional de tres de febrero'], lat: -34.6037, lng: -58.3816, city: 'Buenos Aires', country: 'Argentina' },
    { patterns: ['universidad nacional de asuncion', 'facen', 'fiuna', 'universidad catolica nuestra senora de la asuncion', 'guyra paraguay', 'cedic', 'fundacion manuel gondra', 'tierraviva', 'instituto de investigacion biologica del paraguay'], lat: -25.2637, lng: -57.5759, city: 'Asuncion', country: 'Paraguay' },
    { patterns: ['wwf paraguay', 'ceaduc'], lat: -25.2637, lng: -57.5759, city: 'Asuncion', country: 'Paraguay' },
    { patterns: ['wcs bolivia', 'noel kempff', 'uagrm', 'gabriel moreno', 'observatorio del bosque seco chiquitano', 'santa cruz'], lat: -17.8146, lng: -63.1561, city: 'Santa Cruz de la Sierra', country: 'Bolivia' },
    { patterns: ['cipca cordillera'], lat: -20.0385, lng: -63.5180, city: 'Camiri', country: 'Bolivia' },
    { patterns: ['cipca'], lat: -16.4897, lng: -68.1193, city: 'La Paz', country: 'Bolivia' },
    { patterns: ['ipdrs', 'la paz', 'fundacion tierra'], lat: -16.4897, lng: -68.1193, city: 'La Paz', country: 'Bolivia' },
    { patterns: ['universidad catolica boliviana', 'cochabamba'], lat: -17.3895, lng: -66.1568, city: 'Cochabamba', country: 'Bolivia' },
    { patterns: ['universidade do estado do para'], lat: -1.4558, lng: -48.4902, city: 'Belem', country: 'Brazil' },
    { patterns: ['universidade federal da integracao latino-americana', 'unila'], lat: -25.5163, lng: -54.5854, city: 'Foz do Iguacu', country: 'Brazil' },
    { patterns: ['ufms', 'campo grande'], lat: -20.4697, lng: -54.6201, city: 'Campo Grande', country: 'Brazil' },
    { patterns: ['embrapa pantanal'], lat: -19.0096, lng: -57.6530, city: 'Corumba', country: 'Brazil' },
    { patterns: ['humboldt universitat zu berlin', 'freie universitat berlin', 'thesys', 'geography department, humboldt'], lat: 52.5200, lng: 13.4050, city: 'Berlin', country: 'Germany' },
    { patterns: ['iamo', 'halle-wittenberg', 'martin luther university halle'], lat: 51.4825, lng: 11.9705, city: 'Halle', country: 'Germany' },
    { patterns: ['universitat bonn', 'zef'], lat: 50.7374, lng: 7.0982, city: 'Bonn', country: 'Germany' },
    { patterns: ['ku leuven'], lat: 50.8798, lng: 4.7005, city: 'Leuven', country: 'Belgium' },
    { patterns: ['universitat de barcelona', 'autonoma de barcelona', 'icta'], lat: 41.3874, lng: 2.1686, city: 'Barcelona', country: 'Spain' },
    { patterns: ['universidad de santiago de compostela'], lat: 42.8782, lng: -8.5448, city: 'Santiago de Compostela', country: 'Spain' },
    { patterns: ["ca foscari university of venice"], lat: 45.4408, lng: 12.3155, city: 'Venice', country: 'Italy' },
    { patterns: ['mcgill university'], lat: 45.5048, lng: -73.5772, city: 'Montreal', country: 'Canada' },
    { patterns: ['memorial university of newfoundland'], lat: 47.5615, lng: -52.7126, city: "St. John's", country: 'Canada' },
    { patterns: ['university of british columbia'], lat: 49.2606, lng: -123.2460, city: 'Vancouver', country: 'Canada' },
    { patterns: ['stanford university'], lat: 37.4275, lng: -122.1697, city: 'Stanford, CA', country: 'United States' },
    { patterns: ['university of oregon'], lat: 44.0521, lng: -123.0868, city: 'Eugene, OR', country: 'United States' },
    { patterns: ['university of arizona'], lat: 32.2319, lng: -110.9501, city: 'Tucson, AZ', country: 'United States' },
    { patterns: ['clark university'], lat: 42.2509, lng: -71.8237, city: 'Worcester, MA', country: 'United States' },
    { patterns: ['university of california, berkeley'], lat: 37.8715, lng: -122.2730, city: 'Berkeley, CA', country: 'United States' },
    { patterns: ['university of texas at austin'], lat: 30.2849, lng: -97.7341, city: 'Austin, TX', country: 'United States' },
    { patterns: ['colorado school of mines'], lat: 39.7503, lng: -105.2211, city: 'Golden, CO', country: 'United States' },
    { patterns: ['colorado state university'], lat: 40.5734, lng: -105.0865, city: 'Fort Collins, CO', country: 'United States' },
    { patterns: ['cornell university'], lat: 42.4534, lng: -76.4735, city: 'Ithaca, NY', country: 'United States' },
    { patterns: ['university of georgia'], lat: 33.9480, lng: -83.3773, city: 'Athens, GA', country: 'United States' },
    { patterns: ['appalachian state university'], lat: 36.2139, lng: -81.6842, city: 'Boone, NC', country: 'United States' },
    { patterns: ['prescott college'], lat: 34.5400, lng: -112.4685, city: 'Prescott, AZ', country: 'United States' },
    { patterns: ['university of florida'], lat: 29.6436, lng: -82.3549, city: 'Gainesville, FL', country: 'United States' },
    { patterns: ['brown university'], lat: 41.8268, lng: -71.4025, city: 'Providence, RI', country: 'United States' },
    { patterns: ['depaul university', 'field museum of natural history'], lat: 41.8781, lng: -87.6298, city: 'Chicago, IL', country: 'United States' },
    { patterns: ['university of alabama'], lat: 33.2098, lng: -87.5692, city: 'Tuscaloosa, AL', country: 'United States' },
    { patterns: ['nanyang technological university'], lat: 1.3483, lng: 103.6831, city: 'Singapore', country: 'Singapore' },
    { patterns: ['universite rennes 2', 'arenes'], lat: 48.1173, lng: -1.6778, city: 'Rennes', country: 'France' },
    { patterns: ['sorbonne universite', 'paris cite', 'mondes americains', 'creda'], lat: 48.8566, lng: 2.3522, city: 'Paris', country: 'France' },
    { patterns: ['uclouvain', 'universite catholique de louvain'], lat: 50.6681, lng: 4.6118, city: 'Louvain-la-Neuve', country: 'Belgium' }
    ,
    { patterns: ['birkbeck', 'university of london', 'natural history museum london'], lat: 51.5074, lng: -0.1278, city: 'London', country: 'United Kingdom' },
    { patterns: ['durham university'], lat: 54.7753, lng: -1.5849, city: 'Durham', country: 'United Kingdom' },
    { patterns: ['university of groningen'], lat: 53.2194, lng: 6.5665, city: 'Groningen', country: 'Netherlands' },
    { patterns: ['international institute of social studies', 'erasmus university rotterdam'], lat: 52.0705, lng: 4.3007, city: 'The Hague', country: 'Netherlands' }
  ];

  function clamp(num, min, max) {
    return Math.min(max, Math.max(min, num));
  }

  function getState(container) {
    let state = stateByContainer.get(container);
    if (!state) {
      state = {
        drillClusterId: null,
        selectedDetailBubbleId: null,
        selectedWorldClusterId: null
      };
      stateByContainer.set(container, state);
    }
    return state;
  }

  function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
  }

  function normalizeText(value) {
    return (value || '')
      .toString()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-zA-Z0-9]+/g, ' ')
      .toLowerCase()
      .replace(/\s+/g, ' ')
      .trim();
  }

  function escapeRegex(value) {
    return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function affiliationMatchesPattern(affiliation, pattern) {
    if (!pattern) return false;
    const normalizedPattern = normalizeText(pattern);

    if (!normalizedPattern.includes(' ')) {
      const boundaryRegex = new RegExp(`(^|[^a-z0-9])${escapeRegex(normalizedPattern)}($|[^a-z0-9])`);
      return boundaryRegex.test(affiliation);
    }

    return affiliation.includes(normalizedPattern);
  }

  function getBasePath() {
    const path = window.location.pathname;
    if (path.includes('/site/')) {
      return path.substring(0, path.indexOf('/site/') + 6);
    }
    return './';
  }

  function equalEarthRaw(lat, lng) {
    const lambda = lng * (Math.PI / 180);
    const phi = lat * (Math.PI / 180);
    const theta = Math.asin(M * Math.sin(phi));
    const theta2 = theta * theta;
    const theta6 = theta2 * theta2 * theta2;
    return {
      x: (lambda * Math.cos(theta)) / (M * (A1 + (3 * A2 * theta2) + (theta6 * ((7 * A3) + (9 * A4 * theta2))))),
      y: theta * (A1 + (A2 * theta2) + (theta6 * (A3 + (A4 * theta2))))
    };
  }

  function project(lat, lng) {
    const raw = equalEarthRaw(lat, lng);
    return {
      x: MAP_OFFSET_X + ((raw.x - RAW_X_MIN) * MAP_SCALE),
      y: MAP_OFFSET_Y + ((RAW_Y_MAX - raw.y) * MAP_SCALE)
    };
  }

  function getRenderWidth(container) {
    if (!container) return 1000;
    if (typeof container.clientWidth === 'number' && container.clientWidth > 0) return container.clientWidth;
    if (typeof container.getBoundingClientRect === 'function') {
      const rect = container.getBoundingClientRect();
      if (rect && rect.width) return rect.width;
    }
    return 1000;
  }

  function getWorldClusterThreshold(renderWidth) {
    const width = Math.max(renderWidth || 1000, 320);
    const targetPixels = width >= 1200 ? 16 : width >= 900 ? 18 : width >= 700 ? 22 : 30;
    return clamp((targetPixels * MAP_WIDTH) / width, 12, 56);
  }

  function getWorldCollisionPadding(renderWidth) {
    if (renderWidth >= 1200) return 18;
    if (renderWidth >= 900) return 15;
    if (renderWidth >= 700) return 12;
    return 10;
  }

  function pxToWorldUnits(px, renderWidth) {
    const width = Math.max(renderWidth || 1000, 320);
    return (px * MAP_WIDTH) / width;
  }

  function getSmallScreenMapScale(renderWidth) {
    const width = Math.max(renderWidth || 1000, 320);
    if (width >= 700) return 1;
    return clamp(820 / width, 1, 2.35);
  }

  function applySmallScreenMinimum(baseSize, renderWidth, minScreenPx) {
    const width = Math.max(renderWidth || 1000, 320);
    if (width >= 700) return baseSize;
    return Math.max(baseSize * getSmallScreenMapScale(width), pxToWorldUnits(minScreenPx, width));
  }

  function getWorldBubbleRadius(count, renderWidth) {
    let baseRadius;
    if (count <= 1) baseRadius = 5.8;
    else if (count <= 4) baseRadius = 7.2 + (count * 0.95);
    else if (count <= 12) baseRadius = 10.5 + (count * 0.48);
    else baseRadius = Math.min(16 + (Math.log(count) * 2.5), 21);

    return applySmallScreenMinimum(baseRadius, renderWidth, count <= 1 ? 8 : 10);
  }

  function getWorldTextSize(count, renderWidth) {
    let baseSize;
    if (count <= 9) baseSize = 14;
    else if (count <= 99) baseSize = 13;
    else baseSize = 12;

    return applySmallScreenMinimum(baseSize, renderWidth, 12);
  }

  function getDetailBubbleRadius(count, renderWidth) {
    let baseRadius;
    if (count <= 1) baseRadius = 6;
    else if (count <= 4) baseRadius = 8 + (count * 1.1);
    else if (count <= 12) baseRadius = 11 + (count * 0.65);
    else baseRadius = Math.min(17 + (Math.log(count) * 2.2), 23);

    return applySmallScreenMinimum(baseRadius, renderWidth, count <= 1 ? 8 : 10);
  }

  function getDetailTextSize(count, renderWidth) {
    let baseSize;
    if (count <= 9) baseSize = 14;
    else if (count <= 99) baseSize = 13;
    else baseSize = 12;

    return applySmallScreenMinimum(baseSize, renderWidth, 12);
  }

  const CITY_DISPLAY_OVERRIDES = {
    'cordoba': 'Córdoba',
    'asuncion': 'Asunción',
    'san miguel de tucuman': 'San Miguel de Tucumán',
    'bahia blanca': 'Bahía Blanca',
    'corumba': 'Corumbá',
    'belem': 'Belém',
    'foz do iguacu': 'Foz do Iguaçu',
    'montreal': 'Montréal',
    'the hague': 'The Hague',
    'san carlos de bariloche': 'San Carlos de Bariloche'
  };

  function splitAffiliationSegments(affiliation) {
    return String(affiliation || '')
      .split(/\s+\/\s+|[;|]/)
      .map(segment => normalizeText(segment))
      .filter(Boolean);
  }

  function findAffiliationMatch(researcher, targetCountry, strictCountry = false) {
    const segments = splitAffiliationSegments(researcher.affiliation || '');
    if (!segments.length) return null;

    if (targetCountry) {
      for (const segment of segments) {
        const countryMatch = AFFILIATION_LOCATION_KEYWORDS.find(entry =>
          entry.country === targetCountry &&
          entry.patterns.some(pattern => affiliationMatchesPattern(segment, pattern))
        );
        if (countryMatch) return countryMatch;
      }

      if (strictCountry) return null;
    }

    for (const segment of segments) {
      const anyMatch = AFFILIATION_LOCATION_KEYWORDS.find(entry =>
        entry.patterns.some(pattern => affiliationMatchesPattern(segment, pattern))
      );
      if (anyMatch) return anyMatch;
    }

    return null;
  }

  function getResearcherLocation(researcher, targetCountry = null, options = {}) {
    const allowApproximate = options.allowApproximate !== false;
    const preferredCountry = targetCountry || researcher.country || '';
    const match = findAffiliationMatch(researcher, preferredCountry, Boolean(targetCountry));
    if (match) {
      return {
        lat: match.lat,
        lng: match.lng,
        city: match.city,
        country: match.country || preferredCountry || researcher.country || '',
        isApproximate: false
      };
    }

    const curated = data.collaboratorLocations && data.collaboratorLocations[researcher.id];
    if (curated && typeof curated.lat === 'number' && typeof curated.lng === 'number') {
      if (!preferredCountry || !curated.country || curated.country === preferredCountry) {
        return {
          lat: curated.lat,
          lng: curated.lng,
          city: curated.city || '',
          country: curated.country || preferredCountry || researcher.country || '',
          isApproximate: false
        };
      }
    }

    if (!allowApproximate) {
      return null;
    }

    const country = preferredCountry || researcher.country || '';
    const fallback = data.countryCentroids && data.countryCentroids[country];
    if (fallback && typeof fallback.lat === 'number' && typeof fallback.lng === 'number') {
      return {
        lat: fallback.lat,
        lng: fallback.lng,
        city: '',
        country,
        isApproximate: true
      };
    }

    return null;
  }

  function createPoints(researchers, options = {}) {
    return researchers.map(researcher => {
      const location = getResearcherLocation(researcher, null, options);
      if (!location) return null;
      const projected = project(location.lat, location.lng);
      return {
        researcher,
        id: researcher.id,
        name: researcher.name,
        affiliation: researcher.affiliation || '',
        country: researcher.country || location.country || '',
        city: location.city || '',
        lat: location.lat,
        lng: location.lng,
        isApproximate: Boolean(location.isApproximate),
        locationLabel: location.city ? `${location.city}, ${location.country}` : location.country,
        x: projected.x,
        y: projected.y
      };
    }).filter(Boolean);
  }

  function getCanonicalCityKey(city) {
    return normalizeText(city || '');
  }

  function getDisplayCityName(city) {
    const key = getCanonicalCityKey(city);
    return CITY_DISPLAY_OVERRIDES[key] || city || '';
  }

  function groupBy(items, getKey) {
    const map = new Map();
    items.forEach(item => {
      const key = getKey(item);
      if (!map.has(key)) map.set(key, []);
      map.get(key).push(item);
    });
    return map;
  }

  function getClosestPointOnSegment(px, py, x1, y1, x2, y2) {
    const dx = x2 - x1;
    const dy = y2 - y1;
    const lengthSquared = (dx * dx) + (dy * dy);

    if (lengthSquared < 0.000001) {
      return { x: x1, y: y1, distance: Math.hypot(px - x1, py - y1) };
    }

    const t = clamp((((px - x1) * dx) + ((py - y1) * dy)) / lengthSquared, 0, 1);
    const x = x1 + (dx * t);
    const y = y1 + (dy * t);
    return {
      x,
      y,
      distance: Math.hypot(px - x, py - y)
    };
  }

  function getLeaderSegment(cluster) {
    const dx = cluster.displayX - cluster.anchorX;
    const dy = cluster.displayY - cluster.anchorY;
    const distance = Math.hypot(dx, dy);

    if (distance < 2) return null;

    const ux = dx / distance;
    const uy = dy / distance;
    const bubbleGap = cluster.radius + 1.5;

    return {
      clusterId: cluster.id,
      x1: cluster.anchorX,
      y1: cluster.anchorY,
      x2: cluster.displayX - (ux * bubbleGap),
      y2: cluster.displayY - (uy * bubbleGap),
      dx,
      dy
    };
  }

  function resolveWorldClusterCollisions(clusters, renderWidth) {
    const resolved = clusters.map(cluster => ({ ...cluster }));
    const padding = getWorldCollisionPadding(renderWidth);

    for (let iteration = 0; iteration < 140; iteration += 1) {
      let moved = false;

      for (let i = 0; i < resolved.length; i += 1) {
        for (let j = i + 1; j < resolved.length; j += 1) {
          const a = resolved[i];
          const b = resolved[j];
          let dx = b.displayX - a.displayX;
          let dy = b.displayY - a.displayY;
          let dist = Math.hypot(dx, dy);
          const minDist = a.radius + b.radius + padding;

          if (dist >= minDist) continue;

          if (dist < 0.001) {
            const angle = ((i * 2.399963229728653) + (j * 0.7853981633974483)) % (Math.PI * 2);
            dx = Math.cos(angle);
            dy = Math.sin(angle);
            dist = 1;
          }

          const overlap = (minDist - dist) / 2;
          const ux = dx / dist;
          const uy = dy / dist;
          a.displayX -= ux * overlap;
          a.displayY -= uy * overlap;
          b.displayX += ux * overlap;
          b.displayY += uy * overlap;
          moved = true;
        }
      }

      const leaderSegments = resolved
        .map(cluster => getLeaderSegment(cluster))
        .filter(Boolean);

      resolved.forEach(cluster => {
        leaderSegments.forEach(segment => {
          if (segment.clusterId === cluster.id) return;

          const closest = getClosestPointOnSegment(
            cluster.displayX,
            cluster.displayY,
            segment.x1,
            segment.y1,
            segment.x2,
            segment.y2
          );
          const minDist = cluster.radius + 2.5;

          if (closest.distance >= minDist) return;

          let pushX = cluster.displayX - closest.x;
          let pushY = cluster.displayY - closest.y;
          let pushDistance = Math.hypot(pushX, pushY);

          if (pushDistance < 0.001) {
            const segLength = Math.hypot(segment.dx, segment.dy) || 1;
            pushX = -segment.dy / segLength;
            pushY = segment.dx / segLength;
            pushDistance = 1;
          }

          const overlap = (minDist - closest.distance) + 0.75;
          cluster.displayX += (pushX / pushDistance) * overlap;
          cluster.displayY += (pushY / pushDistance) * overlap;
          moved = true;
        });
      });

      resolved.forEach(cluster => {
        cluster.displayX += (cluster.anchorX - cluster.displayX) * 0.04;
        cluster.displayY += (cluster.anchorY - cluster.displayY) * 0.04;
        const margin = Math.max(16, cluster.radius + 2);
        cluster.displayX = clamp(cluster.displayX, margin, MAP_WIDTH - margin);
        cluster.displayY = clamp(cluster.displayY, margin, MAP_HEIGHT - margin);
      });

      if (!moved) break;
    }

    return resolved.map(cluster => ({
      ...cluster,
      displayX: Number(cluster.displayX.toFixed(2)),
      displayY: Number(cluster.displayY.toFixed(2))
    }));
  }

  function buildWorldClusters(points, researchers, renderWidth) {
    const byCountry = groupBy(points, point => point.country || 'Unknown');
    const researchersByCountry = groupBy(researchers, researcher => researcher.country || 'Unknown');
    const clusters = [];

    byCountry.forEach((countryPoints, country) => {
      const allMembers = (researchersByCountry.get(country) || []).map(researcher => {
        const visiblePoint = countryPoints.find(point => point.id === researcher.id);
        if (visiblePoint) return visiblePoint;
        return {
          researcher,
          id: researcher.id,
          name: researcher.name,
          affiliation: researcher.affiliation || '',
          country: researcher.country || country,
          city: '',
          lat: null,
          lng: null,
          isApproximate: true,
          isHiddenLocation: true,
          locationLabel: researcher.country || country,
          x: null,
          y: null
        };
      });
      const centroid = data.countryCentroids && data.countryCentroids[country];
      const memberCenterX = countryPoints.reduce((sum, point) => sum + point.x, 0) / countryPoints.length;
      const memberCenterY = countryPoints.reduce((sum, point) => sum + point.y, 0) / countryPoints.length;
      const countryAnchor = centroid ? project(centroid.lat, centroid.lng) : null;
      const distinctLocationKeys = new Set(countryPoints.map(point => {
        if (point.city) return `${country}|city|${getCanonicalCityKey(point.city)}`;
        return `${country}|coords|${point.lat.toFixed(4)}|${point.lng.toFixed(4)}`;
      }));
      const hasMultipleDistinctLocations = distinctLocationKeys.size > 1;
      const shouldUseCountryAnchor = Boolean(countryAnchor) && hasMultipleDistinctLocations && (
        WORLD_COUNTRY_ANCHOR_OVERRIDES.has(country) || countryPoints.length > 1
      );
      const anchorX = shouldUseCountryAnchor ? countryAnchor.x : memberCenterX;
      const anchorY = shouldUseCountryAnchor ? countryAnchor.y : memberCenterY;

      clusters.push({
        id: countryPoints.map(member => member.id).sort().join('__'),
        kind: 'world-cluster',
        country,
        count: allMembers.length,
        members: countryPoints,
        allMembers,
        anchorX,
        anchorY,
        displayX: anchorX,
        displayY: anchorY,
        radius: getWorldBubbleRadius(allMembers.length, renderWidth),
        textSize: getWorldTextSize(allMembers.length, renderWidth),
        hitPadding: Math.max(8, pxToWorldUnits(10, renderWidth))
      });
    });

    return resolveWorldClusterCollisions(clusters, renderWidth);
  }

  function buildDetailBubbles(sourceCluster, renderWidth) {
    const detailMembers = sourceCluster.members.map(member => {
      const location = getResearcherLocation(member.researcher || member, sourceCluster.country, { allowApproximate: false });
      if (!location) return null;
      const projected = project(location.lat, location.lng);
      const displayCity = getDisplayCityName(location.city || '');
      return {
        researcher: member.researcher || member,
        id: member.id,
        name: member.name,
        affiliation: (member.researcher && member.researcher.affiliation) || member.affiliation || '',
        country: sourceCluster.country,
        city: displayCity,
        cityKey: getCanonicalCityKey(location.city || ''),
        lat: location.lat,
        lng: location.lng,
        isApproximate: Boolean(location.isApproximate),
        locationLabel: displayCity ? `${displayCity}, ${sourceCluster.country}` : sourceCluster.country,
        x: projected.x,
        y: projected.y
      };
    }).filter(Boolean);

    const byLocation = groupBy(detailMembers, member => {
      if (member.cityKey) {
        return [member.country, member.cityKey].join('|');
      }
      return [member.country, member.lat.toFixed(4), member.lng.toFixed(4)].join('|');
    });

    const bubbles = [];

    byLocation.forEach((members, locationKey) => {
      const first = members[0];
      const avgLat = members.reduce((sum, member) => sum + member.lat, 0) / members.length;
      const avgLng = members.reduce((sum, member) => sum + member.lng, 0) / members.length;
      const projected = project(avgLat, avgLng);
      const displayCity = members.find(member => member.city)?.city || '';
      bubbles.push({
        id: locationKey,
        kind: 'detail-bubble',
        count: members.length,
        members,
        x: projected.x,
        y: projected.y,
        radius: getDetailBubbleRadius(members.length, renderWidth),
        textSize: getDetailTextSize(members.length, renderWidth),
        isApproximate: members.every(member => member.isApproximate),
        locationLabel: displayCity ? `${displayCity}, ${sourceCluster.country}` : sourceCluster.country
      });
    });

    return bubbles.sort((a, b) => b.count - a.count || a.locationLabel.localeCompare(b.locationLabel));
  }

  function buildDetailViewBox(sourceCluster) {
    const detailMembers = sourceCluster.detailMembers || sourceCluster.members;
    const xs = detailMembers.map(member => member.x);
    const ys = detailMembers.map(member => member.y);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);
    const spanX = Math.max(maxX - minX, 0);
    const spanY = Math.max(maxY - minY, 0);

    let width = Math.max(spanX * 1.35, 120);
    let height = Math.max(spanY * 1.4, 90);

    if ((width / height) > MAP_ASPECT) {
      height = width / MAP_ASPECT;
    } else {
      width = height * MAP_ASPECT;
    }

    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;
    let viewX = centerX - (width / 2);
    let viewY = centerY - (height / 2);

    viewX = clamp(viewX, 0, MAP_WIDTH - width);
    viewY = clamp(viewY, 0, MAP_HEIGHT - height);

    return {
      x: Number(viewX.toFixed(2)),
      y: Number(viewY.toFixed(2)),
      width: Number(width.toFixed(2)),
      height: Number(height.toFixed(2))
    };
  }

  function formatViewBox(viewBox) {
    return `${viewBox.x.toFixed(2)} ${viewBox.y.toFixed(2)} ${viewBox.width.toFixed(2)} ${viewBox.height.toFixed(2)}`;
  }

  function getDetailScale(viewBox) {
    return clamp(viewBox.width / MAP_WIDTH, 0.035, 1);
  }

  function resolveDetailBubbleCollisions(bubbles, viewBox, renderWidth) {
    const detailScale = getDetailScale(viewBox);
    const padding = 11 * detailScale;
    const resolved = bubbles.map(bubble => ({
      ...bubble,
      displayX: bubble.x,
      displayY: bubble.y,
      displayRadius: bubble.radius * detailScale,
      displayTextSize: bubble.textSize * detailScale,
      displayHitPadding: Math.max(8 * detailScale, (14 * viewBox.width) / Math.max(renderWidth || 1000, 320))
    }));

    for (let iteration = 0; iteration < 140; iteration += 1) {
      let moved = false;

      for (let i = 0; i < resolved.length; i += 1) {
        for (let j = i + 1; j < resolved.length; j += 1) {
          const a = resolved[i];
          const b = resolved[j];
          let dx = b.displayX - a.displayX;
          let dy = b.displayY - a.displayY;
          let dist = Math.hypot(dx, dy);
          const minDist = a.displayRadius + b.displayRadius + padding;

          if (dist >= minDist) continue;

          if (dist < 0.001) {
            const angle = ((i * 2.399963229728653) + (j * 0.7853981633974483)) % (Math.PI * 2);
            dx = Math.cos(angle);
            dy = Math.sin(angle);
            dist = 1;
          }

          const overlap = (minDist - dist) / 2;
          const ux = dx / dist;
          const uy = dy / dist;
          a.displayX -= ux * overlap;
          a.displayY -= uy * overlap;
          b.displayX += ux * overlap;
          b.displayY += uy * overlap;
          moved = true;
        }
      }

      resolved.forEach(bubble => {
        bubble.displayX += (bubble.x - bubble.displayX) * 0.08;
        bubble.displayY += (bubble.y - bubble.displayY) * 0.08;
        const margin = bubble.displayRadius + (4 * detailScale);
        bubble.displayX = clamp(bubble.displayX, viewBox.x + margin, viewBox.x + viewBox.width - margin);
        bubble.displayY = clamp(bubble.displayY, viewBox.y + margin, viewBox.y + viewBox.height - margin);
      });

      if (!moved) break;
    }

    return resolved.map(bubble => ({
      ...bubble,
      displayX: Number(bubble.displayX.toFixed(2)),
      displayY: Number(bubble.displayY.toFixed(2)),
      displayRadius: Number(bubble.displayRadius.toFixed(3)),
      displayTextSize: Number(bubble.displayTextSize.toFixed(3)),
      displayHitPadding: Number(bubble.displayHitPadding.toFixed(3))
    }));
  }

  function buildWorldModel(researchers, renderWidth) {
    const points = createPoints(researchers, { allowApproximate: false });
    const clusters = buildWorldClusters(points, researchers, renderWidth);
    return {
      mode: 'world',
      renderWidth,
      totalResearchers: researchers.length,
      mappedResearchers: points.length,
      points,
      clusters,
      viewBox: MAP_VIEWBOX
    };
  }

  function buildDetailModel(worldModel, clusterId) {
    const sourceCluster = worldModel.clusters.find(cluster => cluster.id === clusterId);
    if (!sourceCluster) return null;
    const bubbles = buildDetailBubbles(sourceCluster, worldModel.renderWidth);
    const detailMembers = bubbles.flatMap(bubble => bubble.members);
    const detailCluster = {
      ...sourceCluster,
      detailMembers
    };
    const viewBox = buildDetailViewBox(detailCluster);

    return {
      mode: 'detail',
      totalResearchers: worldModel.totalResearchers,
      mappedResearchers: sourceCluster.members.length,
      sourceCluster,
      bubbles: resolveDetailBubbleCollisions(bubbles, viewBox, worldModel.renderWidth),
      viewBox
    };
  }

  function reconcileState(worldModel, state) {
    if (state.drillClusterId && !worldModel.clusters.some(cluster => cluster.id === state.drillClusterId)) {
      state.drillClusterId = null;
      state.selectedDetailBubbleId = null;
    }
    if (state.selectedWorldClusterId && !worldModel.clusters.some(cluster => cluster.id === state.selectedWorldClusterId)) {
      state.selectedWorldClusterId = null;
    }
  }

  function findDetailBubble(model, bubbleId) {
    if (!model || model.mode !== 'detail') return null;
    return model.bubbles.find(bubble => bubble.id === bubbleId) || null;
  }

  function buildModel(researchers, renderWidth, state) {
    const worldModel = buildWorldModel(researchers, renderWidth);
    reconcileState(worldModel, state);

    if (state.drillClusterId) {
      const detailModel = buildDetailModel(worldModel, state.drillClusterId);
      if (detailModel) {
        if (state.selectedDetailBubbleId && !findDetailBubble(detailModel, state.selectedDetailBubbleId)) {
          state.selectedDetailBubbleId = null;
        }
        return detailModel;
      }
    }

    return worldModel;
  }

  function getSelectedIds(model, state) {
    if (!model) return null;
    if (model.mode === 'world') {
      if (!state.selectedWorldClusterId) return null;
      const cluster = model.clusters.find(item => item.id === state.selectedWorldClusterId);
      return cluster ? cluster.allMembers.map(member => member.id) : null;
    }
    if (state.selectedDetailBubbleId) {
      const bubble = findDetailBubble(model, state.selectedDetailBubbleId);
      return bubble ? bubble.members.map(member => member.id) : model.sourceCluster.allMembers.map(member => member.id);
    }
    return model.sourceCluster.allMembers.map(member => member.id);
  }

  function emitSelectionChange(container, model, state, onSelectionChange) {
    const ids = getSelectedIds(model, state);
    if (typeof onSelectionChange === 'function') {
      onSelectionChange(ids);
    }
    if (typeof container.dispatchEvent === 'function' && typeof CustomEvent !== 'undefined') {
      container.dispatchEvent(new CustomEvent('home-map-selectionchange', {
        detail: { ids }
      }));
    }
  }

  function renderLeader(cluster) {
    const segment = getLeaderSegment(cluster);
    if (!segment) return '';

    return `<line class="home-map-leader-line" x1="${segment.x1.toFixed(2)}" y1="${segment.y1.toFixed(2)}" x2="${segment.x2.toFixed(2)}" y2="${segment.y2.toFixed(2)}"></line>`;
  }

  function renderWorldCluster(cluster) {
    const title = cluster.count === 1
      ? `${cluster.allMembers[0].name} - ${((cluster.members[0] && cluster.members[0].locationLabel) || cluster.country)}`
      : `${cluster.count} researchers - ${cluster.country}`;

    return `
      <g class="home-map-cluster${cluster.isSelected ? ' is-selected' : ''}" data-home-map-action="world-cluster" data-cluster-id="${escapeHtml(cluster.id)}">
        <circle class="home-map-cluster-hit" cx="${cluster.displayX.toFixed(2)}" cy="${cluster.displayY.toFixed(2)}" r="${(cluster.radius + (cluster.hitPadding || 8)).toFixed(2)}"></circle>
        <circle class="home-map-cluster-core" cx="${cluster.displayX.toFixed(2)}" cy="${cluster.displayY.toFixed(2)}" r="${cluster.radius.toFixed(2)}"></circle>
        ${cluster.count > 1 ? `<text class="home-map-cluster-count" x="${cluster.displayX.toFixed(2)}" y="${(cluster.displayY + 0.5).toFixed(2)}" style="font-size:${(cluster.textSize || 14).toFixed(2)}px">${cluster.count}</text>` : ''}
        <title>${escapeHtml(title)}</title>
      </g>
    `;
  }

  function shouldDrillIntoCluster(worldModel, clusterId) {
    const detailModel = buildDetailModel(worldModel, clusterId);
    return Boolean(detailModel && detailModel.bubbles.length > 1);
  }

  function renderDetailBubble(bubble, isSelected) {
    const title = bubble.count === 1
      ? `${bubble.members[0].name} - ${bubble.locationLabel}`
      : `${bubble.count} researchers - ${bubble.locationLabel}`;
    const radius = bubble.displayRadius || bubble.radius;
    const hitRadius = radius + (bubble.displayHitPadding || 8);
    const textSize = bubble.displayTextSize || bubble.textSize || 14;
    const x = bubble.displayX || bubble.x;
    const y = bubble.displayY || bubble.y;

    return `
      <g class="home-map-cluster home-map-detail-cluster${isSelected ? ' is-selected' : ''}${bubble.isApproximate ? ' is-approximate' : ''}" data-home-map-action="detail-bubble" data-bubble-id="${escapeHtml(bubble.id)}">
        <circle class="home-map-cluster-hit" cx="${x.toFixed(2)}" cy="${y.toFixed(2)}" r="${hitRadius.toFixed(2)}"></circle>
        <circle class="home-map-cluster-core" cx="${x.toFixed(2)}" cy="${y.toFixed(2)}" r="${radius.toFixed(2)}" style="stroke-width:${(2 * (radius / Math.max(bubble.radius || radius, 0.001))).toFixed(2)}"></circle>
        ${bubble.count > 1 ? `<text class="home-map-cluster-count" x="${x.toFixed(2)}" y="${(y + 0.5).toFixed(2)}" style="font-size:${textSize.toFixed(2)}px">${bubble.count}</text>` : ''}
        <title>${escapeHtml(title)}</title>
      </g>
    `;
  }

  function renderSvg(model, state) {
    const basePath = getBasePath();

    if (model.mode === 'detail') {
      return `
        <svg class="home-map-svg is-detail" viewBox="${formatViewBox(model.viewBox)}" role="img" aria-label="${escapeHtml(I18n.t('home.map_title'))}">
          <image href="${escapeHtml(basePath + 'img/collaborator-world.svg')}" x="0" y="0" width="${MAP_WIDTH}" height="${MAP_HEIGHT}" preserveAspectRatio="none"></image>
          <g class="home-map-cluster-layer">
            ${model.bubbles.map(bubble => renderDetailBubble(bubble, state.selectedDetailBubbleId === bubble.id)).join('')}
          </g>
        </svg>
      `;
    }

    return `
      <svg class="home-map-svg" viewBox="${MAP_VIEWBOX}" role="img" aria-label="${escapeHtml(I18n.t('home.map_title'))}">
        <image href="${escapeHtml(basePath + 'img/collaborator-world.svg')}" x="0" y="0" width="${MAP_WIDTH}" height="${MAP_HEIGHT}" preserveAspectRatio="none"></image>
        <g class="home-map-leader-layer">
          ${model.clusters.map(cluster => renderLeader(cluster)).join('')}
        </g>
        <g class="home-map-cluster-layer">
          ${model.clusters.map(cluster => {
            const isSelected = state.selectedWorldClusterId === cluster.id;
            return renderWorldCluster({
              ...cluster,
              isSelected
            });
          }).join('')}
        </g>
      </svg>
    `;
  }

  function bindEvents(container, researchers, options) {
    const state = getState(container);
    const mapRoot = container.querySelector('.home-map-root');
    if (!mapRoot) return;

    mapRoot.addEventListener('click', (event) => {
      const worldClusterTarget = event.target.closest('[data-home-map-action="world-cluster"]');
      const detailBubbleTarget = event.target.closest('[data-home-map-action="detail-bubble"]');

      if (worldClusterTarget) {
        const clusterId = worldClusterTarget.dataset.clusterId || null;
        const worldModel = buildWorldModel(researchers, getRenderWidth(container));
        if (clusterId && shouldDrillIntoCluster(worldModel, clusterId)) {
          state.drillClusterId = clusterId;
          state.selectedDetailBubbleId = null;
          state.selectedWorldClusterId = null;
        } else {
          state.drillClusterId = null;
          state.selectedDetailBubbleId = null;
          state.selectedWorldClusterId = state.selectedWorldClusterId === clusterId ? null : clusterId;
        }
        const renderResult = render(container, researchers, options);
        emitSelectionChange(container, renderResult.model, state, options.onSelectionChange);
        return;
      }

      if (detailBubbleTarget) {
        const bubbleId = detailBubbleTarget.dataset.bubbleId || '';
        state.selectedDetailBubbleId = state.selectedDetailBubbleId === bubbleId ? null : bubbleId;
        const renderResult = render(container, researchers, options);
        emitSelectionChange(container, renderResult.model, state, options.onSelectionChange);
        return;
      }

      if (!event.target.closest('.home-map-svg')) return;
      if (!state.drillClusterId && !state.selectedWorldClusterId) return;

      state.drillClusterId = null;
      state.selectedDetailBubbleId = null;
      state.selectedWorldClusterId = null;
      const renderResult = render(container, researchers, options);
      emitSelectionChange(container, renderResult.model, state, options.onSelectionChange);
    });
  }

  function render(container, researchers, options = {}) {
    if (!container) return { selectedIds: null, model: null };

    const state = getState(container);
    const renderWidth = getRenderWidth(container);
    const model = buildModel(researchers, renderWidth, state);

    container.innerHTML = `
      <div class="home-map-root">
        <div class="home-map-frame">
          ${renderSvg(model, state)}
        </div>
      </div>
    `;

    bindEvents(container, researchers, options);
    return {
      model,
      selectedIds: getSelectedIds(model, state)
    };
  }

  function reset(container) {
    if (!container) return;
    const state = getState(container);
    state.drillClusterId = null;
    state.selectedDetailBubbleId = null;
    state.selectedWorldClusterId = null;
  }

  return {
    render,
    reset
  };
})();
