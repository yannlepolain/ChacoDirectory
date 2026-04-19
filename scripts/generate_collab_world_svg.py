#!/usr/bin/env python3

import json
import math
import sys
from pathlib import Path


WIDTH = 1000
HEIGHT = 500
PADDING_X = 8

# Equal Earth projection coefficients.
A1 = 1.340264
A2 = -0.081106
A3 = 0.000893
A4 = 0.003796
M = math.sqrt(3) / 2

RAW_X_MAX = 2.7066299836960748
RAW_Y_MAX = 1.3173627591574133
RAW_X_MIN = -RAW_X_MAX
RAW_Y_MIN = -RAW_Y_MAX

SCALE = (WIDTH - (PADDING_X * 2)) / (RAW_X_MAX - RAW_X_MIN)
PROJECTED_HEIGHT = (RAW_Y_MAX - RAW_Y_MIN) * SCALE
OFFSET_X = PADDING_X
OFFSET_Y = (HEIGHT - PROJECTED_HEIGHT) / 2

DEFAULT_INPUT = Path("/tmp/world-110m-countries.geojson")
DEFAULT_OUTPUT = Path("site/img/collaborator-world.svg")


def equal_earth_raw(lat, lng):
    lam = math.radians(lng)
    phi = math.radians(lat)
    theta = math.asin(M * math.sin(phi))
    theta2 = theta * theta
    theta6 = theta2 * theta2 * theta2
    x = (lam * math.cos(theta)) / (M * (A1 + (3 * A2 * theta2) + (theta6 * ((7 * A3) + (9 * A4 * theta2)))))
    y = theta * (A1 + (A2 * theta2) + (theta6 * (A3 + (A4 * theta2))))
    return x, y


def project(lat, lng):
    raw_x, raw_y = equal_earth_raw(lat, lng)
    x = OFFSET_X + ((raw_x - RAW_X_MIN) * SCALE)
    y = OFFSET_Y + ((RAW_Y_MAX - raw_y) * SCALE)
    return x, y


def fmt(value):
    return f"{value:.2f}"


def ring_to_path(ring):
    commands = []
    started = False
    prev_lng = None
    prev_x = None
    prev_y = None

    for lng, lat in ring:
      x, y = project(lat, lng)
      jump = prev_lng is not None and abs(lng - prev_lng) > 180
      if jump or not started:
          commands.append(f"M {fmt(x)} {fmt(y)}")
          started = True
      else:
          if prev_x is None or abs(x - prev_x) > 0.15 or abs(y - prev_y) > 0.15:
              commands.append(f"L {fmt(x)} {fmt(y)}")
      prev_lng = lng
      prev_x = x
      prev_y = y

    if started:
        commands.append("Z")

    return " ".join(commands)


def geometry_to_paths(geometry):
    geom_type = geometry.get("type")
    coordinates = geometry.get("coordinates", [])

    if geom_type == "Polygon":
        return [ring_to_path(ring) for ring in coordinates if ring]
    if geom_type == "MultiPolygon":
        paths = []
        for polygon in coordinates:
            for ring in polygon:
                if ring:
                    paths.append(ring_to_path(ring))
        return paths
    return []


def build_boundary_path():
    points = []
    for lat in range(-90, 91):
        points.append(project(lat, -180))
    for lat in range(90, -91, -1):
        points.append(project(lat, 180))
    commands = [f"M {fmt(points[0][0])} {fmt(points[0][1])}"]
    commands.extend(f"L {fmt(x)} {fmt(y)}" for x, y in points[1:])
    commands.append("Z")
    return " ".join(commands)


def render_svg(geojson):
    paths = []
    for feature in geojson.get("features", []):
        properties = feature.get("properties") or {}
        if properties.get("name") == "Antarctica" or properties.get("admin") == "Antarctica":
            continue
        geometry = feature.get("geometry") or {}
        paths.extend(geometry_to_paths(geometry))

    boundary_path = build_boundary_path()
    land_paths = "\n".join(f'    <path d="{path}" />' for path in paths if path)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">Political world basemap</title>
  <desc id="desc">Equal Earth political world map with country boundaries for collaborator locations.</desc>
  <defs>
    <linearGradient id="ocean" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stop-color="#f7f3ec" />
      <stop offset="100%" stop-color="#efe8da" />
    </linearGradient>
    <clipPath id="sphere">
      <path d="{boundary_path}" />
    </clipPath>
  </defs>
  <rect width="{WIDTH}" height="{HEIGHT}" fill="#f6f1e6" />
  <path d="{boundary_path}" fill="url(#ocean)" stroke="#d8cfbf" stroke-width="1.2" />
  <g clip-path="url(#sphere)" fill="#d8d1c4" stroke="#fffdf8" stroke-width="0.9">
{land_paths}
  </g>
</svg>
"""


def main():
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT

    if not input_path.exists():
        raise SystemExit(f"Input GeoJSON not found: {input_path}")

    with input_path.open("r", encoding="utf-8") as handle:
        geojson = json.load(handle)

    svg = render_svg(geojson)
    output_path.write_text(svg, encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
