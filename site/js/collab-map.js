const ChacoCollabMap = (() => {
  const data = window.ChacoCollabMapData || {};
  const MAP_WIDTH = data.mapWidth || 1000;
  const MAP_HEIGHT = data.mapHeight || 500;
  const MAP_ASPECT = MAP_WIDTH / MAP_HEIGHT;

  // Equal Earth projection coefficients from the published formulation.
  const A1 = 1.340264;
  const A2 = -0.081106;
  const A3 = 0.000893;
  const A4 = 0.003796;
  const M = Math.sqrt(3) / 2;

  // Raw Equal Earth world bounds on a unit sphere.
  const RAW_X_MAX = 2.7066299836960748;
  const RAW_Y_MAX = 1.3173627591574133;
  const RAW_X_MIN = -RAW_X_MAX;
  const RAW_Y_MIN = -RAW_Y_MAX;

  const MAP_PADDING_X = 8;
  const MAP_SCALE = (MAP_WIDTH - (MAP_PADDING_X * 2)) / (RAW_X_MAX - RAW_X_MIN);
  const PROJECTED_HEIGHT = (RAW_Y_MAX - RAW_Y_MIN) * MAP_SCALE;
  const MAP_OFFSET_X = MAP_PADDING_X;
  const MAP_OFFSET_Y = (MAP_HEIGHT - PROJECTED_HEIGHT) / 2;
  const MAP_IMAGE_X = 0;
  const MAP_IMAGE_Y = 0;
  const MAP_IMAGE_WIDTH = MAP_WIDTH;
  const MAP_IMAGE_HEIGHT = MAP_HEIGHT;

  function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
  }

  function getBasePath() {
    const path = window.location.pathname;
    if (path.includes('/site/')) {
      return path.substring(0, path.indexOf('/site/') + 6);
    }
    return './';
  }

  function resolveCollaborator(reference, allResearchers) {
    if (typeof ChacoData !== 'undefined' && typeof ChacoData.resolveResearcherRef === 'function') {
      return ChacoData.resolveResearcherRef(reference);
    }
    return allResearchers.find(r => r.name === reference || r.id === reference) || null;
  }

  function getLocationForResearcher(researcher) {
    const curated = data.collaboratorLocations && data.collaboratorLocations[researcher.id];
    if (curated && typeof curated.lat === 'number' && typeof curated.lng === 'number') {
      return {
        lat: curated.lat,
        lng: curated.lng,
        city: curated.city || '',
        country: curated.country || researcher.country || '',
        isApproximate: false
      };
    }

    const country = researcher.country || '';
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

  function clamp(num, min, max) {
    return Math.min(max, Math.max(min, num));
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

  function normalizeViewBox(box) {
    let { x, y, width, height } = box;
    width = clamp(width, 140, MAP_WIDTH);
    height = clamp(height, 70, MAP_HEIGHT);

    const ratio = width / height;
    if (ratio > MAP_ASPECT) {
      const neededHeight = width / MAP_ASPECT;
      y -= (neededHeight - height) / 2;
      height = neededHeight;
    } else {
      const neededWidth = height * MAP_ASPECT;
      x -= (neededWidth - width) / 2;
      width = neededWidth;
    }

    x = clamp(x, 0, MAP_WIDTH - width);
    y = clamp(y, 0, MAP_HEIGHT - height);

    return {
      x: Number(x.toFixed(2)),
      y: Number(y.toFixed(2)),
      width: Number(width.toFixed(2)),
      height: Number(height.toFixed(2))
    };
  }

  function computeViewBox(points) {
    if (!points || points.length === 0) {
      return { x: 0, y: 0, width: MAP_WIDTH, height: MAP_HEIGHT };
    }

    if (points.length === 1) {
      const point = points[0];
      return normalizeViewBox({
        x: point.x - 110,
        y: point.y - 55,
        width: 220,
        height: 110
      });
    }

    const xs = points.map(p => p.x);
    const ys = points.map(p => p.y);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);
    const pad = 44;

    return normalizeViewBox({
      x: minX - pad,
      y: minY - pad,
      width: (maxX - minX) + (pad * 2),
      height: (maxY - minY) + (pad * 2)
    });
  }

  function distanceBetweenPoints(a, b) {
    const dx = a.x - b.x;
    const dy = a.y - b.y;
    return Math.sqrt((dx * dx) + (dy * dy));
  }

  function distanceBetweenGroups(a, b) {
    const dx = a.displayX - b.displayX;
    const dy = a.displayY - b.displayY;
    return Math.sqrt((dx * dx) + (dy * dy));
  }

  function getPointRadius(point) {
    return point.isApproximate ? 10 : 12;
  }

  function getStackRadius(group) {
    return clamp(18 + Math.min(group.count * 1.8, 10), 18, 28);
  }

  function getGroupMarkerRadius(group) {
    if (group.kind === 'stack') {
      return group.stackRadius || getStackRadius(group);
    }
    return getPointRadius(group.points[0]);
  }

  function buildInitialGroups(points) {
    const grouped = new Map();

    points.forEach(point => {
      const key = `${point.lat.toFixed(4)}|${point.lng.toFixed(4)}|${point.isApproximate ? 'a' : 'p'}`;
      if (!grouped.has(key)) {
        grouped.set(key, []);
      }
      grouped.get(key).push(point);
    });

    return Array.from(grouped.values()).map((items, index) => {
      const kind = items.length > 1 ? 'stack' : 'single';
      const stackRadius = kind === 'stack' ? getStackRadius({ count: items.length }) : null;
      return {
        id: `${kind}-${index}`,
        kind,
        x: items[0].x,
        y: items[0].y,
        anchorX: items[0].x,
        anchorY: items[0].y,
        displayX: items[0].x,
        displayY: items[0].y,
        count: items.length,
        stackRadius,
        points: items
      };
    });
  }

  function getRequiredSeparation(a, b) {
    return getGroupMarkerRadius(a) + getGroupMarkerRadius(b) + 12;
  }

  function resolveCollisions(groups) {
    if (groups.length <= 1) return groups;

    const resolved = groups.map(group => ({
      ...group,
      displayX: group.x,
      displayY: group.y
    }));

    for (let iteration = 0; iteration < 120; iteration += 1) {
      let moved = false;

      for (let i = 0; i < resolved.length; i += 1) {
        for (let j = i + 1; j < resolved.length; j += 1) {
          const a = resolved[i];
          const b = resolved[j];
          let dx = b.displayX - a.displayX;
          let dy = b.displayY - a.displayY;
          let dist = Math.sqrt((dx * dx) + (dy * dy));
          const minDist = getRequiredSeparation(a, b);

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

      resolved.forEach(group => {
        group.displayX += (group.anchorX - group.displayX) * 0.08;
        group.displayY += (group.anchorY - group.displayY) * 0.08;
        group.displayX = clamp(group.displayX, 16, MAP_WIDTH - 16);
        group.displayY = clamp(group.displayY, 16, MAP_HEIGHT - 16);
      });

      if (!moved) break;
    }

    for (let iteration = 0; iteration < 24; iteration += 1) {
      let changed = false;

      for (let i = 0; i < resolved.length; i += 1) {
        for (let j = i + 1; j < resolved.length; j += 1) {
          const a = resolved[i];
          const b = resolved[j];
          let dx = b.displayX - a.displayX;
          let dy = b.displayY - a.displayY;
          let dist = Math.sqrt((dx * dx) + (dy * dy));
          const minDist = getRequiredSeparation(a, b);

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
          b.displayX += ux * overlap;
          a.displayY -= uy * overlap;
          b.displayY += uy * overlap;
          a.displayX = clamp(a.displayX, 16, MAP_WIDTH - 16);
          a.displayY = clamp(a.displayY, 16, MAP_HEIGHT - 16);
          b.displayX = clamp(b.displayX, 16, MAP_WIDTH - 16);
          b.displayY = clamp(b.displayY, 16, MAP_HEIGHT - 16);
          changed = true;
        }
      }

      if (!changed) break;
    }

    return resolved.map(group => ({
      ...group,
      displayX: Number(group.displayX.toFixed(2)),
      displayY: Number(group.displayY.toFixed(2))
    }));
  }

  function orientStack(group, groups) {
    if (group.kind !== 'stack') return group;

    const neighbors = groups
      .filter(other => other !== group)
      .map(other => ({ other, dist: distanceBetweenGroups(group, other) }))
      .sort((a, b) => a.dist - b.dist);

    const nearest = neighbors[0] || null;
    const radiusBase = 46 + (group.count * 6);
    const radius = clamp(
      nearest ? Math.min(radiusBase, Math.max(46, (nearest.dist * 0.75) - 10)) : radiusBase,
      46,
      96
    );

    let expandedPoints;
    if (nearest && nearest.dist < 180) {
      const awayAngle = Math.atan2(group.displayY - nearest.other.displayY, group.displayX - nearest.other.displayX);
      const spread = Math.min(Math.PI * 1.32, Math.PI * (0.72 + (group.count * 0.14)));
      const start = awayAngle - (spread / 2);
      const step = group.count === 1 ? 0 : spread / Math.max(group.count - 1, 1);
      expandedPoints = group.points.map((item, itemIndex) => {
        const angle = start + (step * itemIndex);
        return {
          ...item,
          expandedX: group.displayX + (Math.cos(angle) * radius),
          expandedY: group.displayY + (Math.sin(angle) * radius)
        };
      });
    } else {
      expandedPoints = group.points.map((item, itemIndex) => {
        const angle = (-Math.PI / 2) + ((Math.PI * 2 * itemIndex) / group.points.length);
        return {
          ...item,
          expandedX: group.displayX + (Math.cos(angle) * radius),
          expandedY: group.displayY + (Math.sin(angle) * radius)
        };
      });
    }

    return {
      ...group,
      radius,
      points: expandedPoints
    };
  }

  function groupPoints(points) {
    const initialGroups = buildInitialGroups(points);
    const separatedGroups = resolveCollisions(initialGroups);
    return separatedGroups.map(group => orientStack(group, separatedGroups));
  }

  function estimateLabelWidth(text) {
    const length = (text || '').length;
    return clamp(30 + (length * 12), 70, 280);
  }

  function clampLabelPosition(x, y, anchor, labelWidth, viewBox) {
    const minX = viewBox ? viewBox.x + 8 : 8;
    const maxX = viewBox ? viewBox.x + viewBox.width - 8 : MAP_WIDTH - 8;
    const minY = viewBox ? viewBox.y + 24 : 24;
    const maxY = viewBox ? viewBox.y + viewBox.height - 12 : MAP_HEIGHT - 12;
    let clampedX = x;
    const clampedY = clamp(y, minY, maxY);

    if (anchor === 'start') {
      clampedX = clamp(x, minX, maxX - labelWidth);
    } else if (anchor === 'end') {
      clampedX = clamp(x, minX + labelWidth, maxX);
    } else {
      clampedX = clamp(x, minX + (labelWidth / 2), maxX - (labelWidth / 2));
    }

    return { x: clampedX, y: clampedY };
  }

  function computeExpandedBounds(groups) {
    const xs = [];
    const ys = [];

    groups.forEach(group => {
      xs.push(group.anchorX, group.displayX);
      ys.push(group.anchorY, group.displayY);

      if (group.kind === 'single') {
        return;
      }

      group.points.forEach(point => {
        xs.push(point.expandedX);
        ys.push(point.expandedY);
      });
    });

    if (!xs.length || !ys.length) {
      return { x: 0, y: 0, width: MAP_WIDTH, height: MAP_HEIGHT };
    }

    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);
    const pad = 84;

    return normalizeViewBox({
      x: minX - pad,
      y: minY - pad,
      width: (maxX - minX) + (pad * 2),
      height: (maxY - minY) + (pad * 2)
    });
  }

  function getFullWorldViewBox() {
    return {
      x: 0,
      y: 0,
      width: MAP_WIDTH,
      height: MAP_HEIGHT
    };
  }

  function getLabelRect(x, y, anchor, labelWidth) {
    const labelHeight = 34;
    if (anchor === 'end') {
      return {
        left: x - labelWidth,
        right: x,
        top: y - labelHeight,
        bottom: y + 8
      };
    }
    if (anchor === 'middle') {
      return {
        left: x - (labelWidth / 2),
        right: x + (labelWidth / 2),
        top: y - labelHeight,
        bottom: y + 8
      };
    }
    return {
      left: x,
      right: x + labelWidth,
      top: y - labelHeight,
      bottom: y + 8
    };
  }

  function pointToRectDistance(px, py, rect) {
    const dx = Math.max(rect.left - px, 0, px - rect.right);
    const dy = Math.max(rect.top - py, 0, py - rect.bottom);
    return Math.sqrt((dx * dx) + (dy * dy));
  }

  function chooseSingleLabelPlacement(group, groups, label, viewBox) {
    const labelWidth = estimateLabelWidth(label);
    const radius = getPointRadius(group.points[0]);
    const offset = radius + 18;
    const candidates = [
      {
        anchor: 'start',
        x: group.displayX + offset,
        y: group.displayY - 16
      },
      {
        anchor: 'end',
        x: group.displayX - offset,
        y: group.displayY - 16
      },
      {
        anchor: 'middle',
        x: group.displayX,
        y: group.displayY - offset
      },
      {
        anchor: 'middle',
        x: group.displayX,
        y: group.displayY + offset + 22
      }
    ];

    let best = null;

    candidates.forEach(candidate => {
      const clamped = clampLabelPosition(candidate.x, candidate.y, candidate.anchor, labelWidth, viewBox);
      const rect = getLabelRect(clamped.x, clamped.y, candidate.anchor, labelWidth);

      const clearance = groups
        .filter(other => other !== group)
        .map(other => pointToRectDistance(other.displayX, other.displayY, rect) - getGroupMarkerRadius(other))
        .reduce((min, value) => Math.min(min, value), Infinity);

      const ownClearance = pointToRectDistance(group.displayX, group.displayY, rect) - radius;
      const centerBias = Math.abs((rect.left + rect.right) / 2 - group.displayX) + (Math.abs((rect.top + rect.bottom) / 2 - group.displayY) * 0.15);
      const score = Math.min(clearance, ownClearance) - (centerBias * 0.01);

      if (!best || score > best.score) {
        best = {
          score,
          anchor: candidate.anchor,
          x: clamped.x,
          y: clamped.y
        };
      }
    });

    return best || { anchor: 'start', x: group.displayX + offset, y: group.displayY - 16 };
  }

  function buildModelForResearcher(researcher, allResearchers) {
    const refs = (researcher.main_collaborators && researcher.main_collaborators.length > 0)
      ? researcher.main_collaborators
      : (researcher.top_collaborators_from_seed || []);

    if (!refs.length) return null;

    const seen = new Set();
    const points = [];

    refs.forEach(reference => {
      const match = resolveCollaborator(reference, allResearchers);
      if (!match || seen.has(match.id)) return;
      seen.add(match.id);

      const location = getLocationForResearcher(match);
      if (!location) return;

      const projected = project(location.lat, location.lng);
      const label = location.city ? `${location.city}, ${location.country}` : location.country;

      points.push({
        id: match.id,
        name: match.name,
        profileUrl: `profile.html?id=${encodeURIComponent(match.id)}`,
        x: projected.x,
        y: projected.y,
        lat: location.lat,
        lng: location.lng,
        city: location.city,
        country: location.country,
        label,
        isApproximate: location.isApproximate
      });
    });

    if (!points.length) return null;

    const groups = groupPoints(points);
    const approximateCount = points.filter(point => point.isApproximate).length;

    return {
      points,
      groups,
      stackCount: groups.filter(group => group.kind === 'stack').length,
      approximateCount,
      totalReferences: refs.length,
      viewBox: getFullWorldViewBox()
    };
  }

  function renderLeaderLine(group) {
    const leaderDistance = distanceBetweenPoints(
      { x: group.anchorX, y: group.anchorY },
      { x: group.displayX, y: group.displayY }
    );

    if (leaderDistance < 3) return '';

    return `
      <line class="collab-map-leader-line" x1="${group.anchorX.toFixed(2)}" y1="${group.anchorY.toFixed(2)}" x2="${group.displayX.toFixed(2)}" y2="${group.displayY.toFixed(2)}"></line>
    `;
  }

  function renderSinglePoint(group, index, totalPointCount, viewBox, allGroups) {
    const point = group.points[0];
    const showLabels = totalPointCount <= 3;
    const titleBits = [
      point.name,
      point.label
    ];
    if (point.isApproximate) {
      titleBits.push(I18n.t('profile.collab_map_approx_point'));
    }
    const label = point.name.split(',')[0];
    const placement = chooseSingleLabelPlacement(group, allGroups, label, viewBox);
    const radius = getPointRadius(point);

    return `
      <g class="collab-map-point${point.isApproximate ? ' is-approximate' : ''}">
        ${renderLeaderLine(group)}
        <a href="${escapeHtml(point.profileUrl)}">
          <circle cx="${group.displayX.toFixed(2)}" cy="${group.displayY.toFixed(2)}" r="${radius.toFixed(2)}"></circle>
          <title>${escapeHtml(titleBits.join(' — '))}</title>
        </a>
        <text class="${showLabels ? 'collab-map-label is-always-visible' : 'collab-map-label'}" x="${placement.x.toFixed(2)}" y="${placement.y.toFixed(2)}" text-anchor="${placement.anchor}">${escapeHtml(label)}</text>
      </g>
    `;
  }

  function renderStack(group, viewBox) {
    const stackTitle = group.points.map(point => point.name).join(', ');
    const children = group.points.map(point => {
      const titleBits = [
        point.name,
        point.label
      ];
      if (point.isApproximate) {
        titleBits.push(I18n.t('profile.collab_map_approx_point'));
      }
      const dx = point.expandedX - group.displayX;
      const dy = point.expandedY - group.displayY;
      const label = point.name.split(',')[0];
      const labelWidth = estimateLabelWidth(label);
      let labelX = point.expandedX;
      let labelY = point.expandedY;
      let textAnchor = 'start';

      if (Math.abs(dx) < 8) {
        textAnchor = 'middle';
        labelX = point.expandedX;
        labelY = point.expandedY + (dy < 0 ? -16 : 24);
      } else if (dx < 0) {
        textAnchor = 'end';
        labelX = point.expandedX - 14;
        labelY = point.expandedY - 10;
      } else {
        textAnchor = 'start';
        labelX = point.expandedX + 14;
        labelY = point.expandedY - 10;
      }

      const clamped = clampLabelPosition(labelX, labelY, textAnchor, labelWidth, viewBox);

      return `
        <g class="collab-map-point collab-map-spider-point${point.isApproximate ? ' is-approximate' : ''}">
          <line class="collab-map-spider-line" x1="${group.displayX.toFixed(2)}" y1="${group.displayY.toFixed(2)}" x2="${point.expandedX.toFixed(2)}" y2="${point.expandedY.toFixed(2)}"></line>
          <a href="${escapeHtml(point.profileUrl)}">
            <circle cx="${point.expandedX.toFixed(2)}" cy="${point.expandedY.toFixed(2)}" r="${getPointRadius(point).toFixed(2)}"></circle>
            <title>${escapeHtml(titleBits.join(' — '))}</title>
          </a>
          <text x="${clamped.x.toFixed(2)}" y="${clamped.y.toFixed(2)}" text-anchor="${textAnchor}">${escapeHtml(label)}</text>
        </g>
      `;
    }).join('');

    const stackRadius = group.stackRadius || getStackRadius(group);
    const hitRadius = stackRadius + 12;

    return `
      <g class="collab-map-stack" tabindex="0">
        <title>${escapeHtml(`${group.count} collaborators: ${stackTitle}`)}</title>
        ${renderLeaderLine(group)}
        <circle class="collab-map-stack-hit" cx="${group.displayX.toFixed(2)}" cy="${group.displayY.toFixed(2)}" r="${hitRadius.toFixed(2)}"></circle>
        <circle class="collab-map-stack-core" cx="${group.displayX.toFixed(2)}" cy="${group.displayY.toFixed(2)}" r="${stackRadius.toFixed(2)}"></circle>
        <text class="collab-map-stack-count" x="${group.displayX.toFixed(2)}" y="${(group.displayY + 0.5).toFixed(2)}">${group.count}</text>
        <g class="collab-map-stack-children">
          ${children}
        </g>
      </g>
    `;
  }

  function renderPoints(model) {
    let singleIndex = 0;
    return model.groups.map(group => {
      if (group.kind === 'stack') {
        return renderStack(group, model.viewBox);
      }
      const markup = renderSinglePoint(group, singleIndex, model.points.length, model.viewBox, model.groups);
      singleIndex += 1;
      return markup;
    }).join('');
  }

  function renderSvg(model) {
    const basePath = getBasePath();
    const clipId = `collab-map-clip-${Math.random().toString(36).slice(2, 10)}`;
    return `
      <svg class="collab-map-svg" viewBox="${model.viewBox.x} ${model.viewBox.y} ${model.viewBox.width} ${model.viewBox.height}" role="img" aria-label="${escapeHtml(I18n.t('profile.collab_map'))}">
        <defs>
          <clipPath id="${clipId}" clipPathUnits="userSpaceOnUse">
            <rect x="${model.viewBox.x}" y="${model.viewBox.y}" width="${model.viewBox.width}" height="${model.viewBox.height}"></rect>
          </clipPath>
        </defs>
        <g clip-path="url(#${clipId})">
          <image href="${escapeHtml(basePath + 'img/collaborator-world.svg')}" x="${MAP_IMAGE_X}" y="${MAP_IMAGE_Y}" width="${MAP_IMAGE_WIDTH}" height="${MAP_IMAGE_HEIGHT}" preserveAspectRatio="none"></image>
          ${renderPoints(model)}
        </g>
      </svg>
    `;
  }

  function render(container, researcher, allResearchers) {
    const model = buildModelForResearcher(researcher, allResearchers);
    if (!container || !model) {
      if (container) container.innerHTML = '';
      return null;
    }

    container.innerHTML = `
      <div class="collab-map-block">
        <div class="collab-map-header-row">
          <div class="collab-map-title">${escapeHtml(I18n.t('profile.collab_map'))}</div>
          <button type="button" class="collab-map-toggle" aria-expanded="false">${escapeHtml(I18n.t('profile.collab_map_show'))}</button>
        </div>
        <div class="collab-map-panel" hidden>
          <div class="collab-map-frame">
            ${renderSvg(model)}
          </div>
          ${model.approximateCount > 0 ? `<p class="collab-map-note">${escapeHtml(I18n.t('profile.collab_map_approx'))}</p>` : ''}
        </div>
      </div>
    `;

    const toggle = container.querySelector('.collab-map-toggle');
    const panel = container.querySelector('.collab-map-panel');
    if (toggle && panel) {
      toggle.addEventListener('click', () => {
        const expanded = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', String(!expanded));
        toggle.textContent = I18n.t(expanded ? 'profile.collab_map_show' : 'profile.collab_map_hide');
        panel.hidden = expanded;
      });
    }

    return model;
  }

  return {
    buildModelForResearcher,
    computeViewBox,
    render
  };
})();
