// Programmatic checks that a comic's lettering looks reasonable: the text
// fits in its panel and keeps off the art, balloons enclose their text with
// room to spare and are smooth, and tails point at their speakers from
// nearby without running into anything. checkComic runs them on what
// drawComic reports drawing.

import { openAt } from "./comic.js";

// Each check's problems are {check, detail}.
function problem(check, detail) {
  return { check, detail };
}

function inside(polygon, [px, py]) {
  let result = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const [xi, yi] = polygon[i];
    const [xj, yj] = polygon[j];
    if (yi > py !== yj > py && px < ((xj - xi) * (py - yi)) / (yj - yi) + xi) {
      result = !result;
    }
  }
  return result;
}

// The box the capital letters of a line occupy (a line's box also includes
// the space between lines).
function capBox(line, cap) {
  const top = line.y + (line.height - cap) / 2;
  return [line.x, top, line.x + line.width, top + cap];
}

function distanceToBox([px, py], [x0, y0, x1, y1]) {
  const dx = Math.max(x0 - px, 0, px - x1);
  const dy = Math.max(y0 - py, 0, py - y1);
  return Math.hypot(dx, dy);
}

// The outline with extra points along any edge longer than `spacing`.
function densify(points, spacing) {
  const out = [];
  for (let i = 0; i < points.length; i++) {
    const a = points[i];
    const b = points[(i + 1) % points.length];
    const pieces = Math.max(1, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) / spacing));
    for (let k = 0; k < pieces; k++) {
      out.push([a[0] + ((b[0] - a[0]) * k) / pieces, a[1] + ((b[1] - a[1]) * k) / pieces]);
    }
  }
  return out;
}

// The outline with points closer than `spacing` to the last one dropped.
function resample(points, spacing) {
  const out = [points[0]];
  for (const p of points) {
    const last = out[out.length - 1];
    if (Math.hypot(p[0] - last[0], p[1] - last[1]) >= spacing) out.push(p);
  }
  return out;
}

function angleBetween([ax, ay], [bx, by]) {
  const cos = (ax * bx + ay * by) / (Math.hypot(ax, ay) * Math.hypot(bx, by));
  return (Math.acos(Math.max(-1, Math.min(1, cos))) * 180) / Math.PI;
}

// Thresholds, in cap heights or degrees.
export const LIMITS = {
  // Space between the lettering and the balloon line. Rounded corners come
  // in closest, and the default text's first balloon (which looks right)
  // comes within 0.28 at one.
  clearance: 0.25,
  // Share of the visible balloon outline that may lie on the art.
  outlineOnArt: 0.1,
  // Sharpest turn in the visible outline, in degrees, between points a
  // quarter of a cap apart.
  turn: 30,
  // How far a tail may point away from its speaker, in degrees.
  aim: 35,
  // How much open space there may be between the end of a tail and the
  // speaker: beyond that, the balloon is stranded.
  reach: 6,
  // How long a tail may be, in caps, when its balloon is already within
  // this of the art (usually the speaker): any longer and it's a needle
  // reaching past them to their mouth.
  tailLength: 2,
};

// Whether there's any art within `radius` of a point.
function artWithin([px, py], radius, step, open) {
  for (let r = step; r <= radius; r += step) {
    const n = Math.max(8, Math.ceil((2 * Math.PI * r) / step));
    for (let k = 0; k < n; k++) {
      const a = (2 * Math.PI * k) / n;
      if (!open([px + r * Math.cos(a), py + r * Math.sin(a)])) return true;
    }
  }
  return false;
}

// Problems with one speech: {who, lines, speaker, outline, tail, stroke},
// in a panel {width, height}, with `others` the other speeches in the
// panel. open(point) says whether a point is clear of the art; style is
// "balloon" or "loose".
export function checkSpeech(speech, others, { cap, panel, open, style, smoothness = false }) {
  const problems = [];
  const { lines, speaker } = speech;
  if (!lines.length) return problems;
  const boxes = lines.map((l) => capBox(l, cap));

  for (const [x0, y0, x1, y1] of boxes) {
    if (x0 < 0 || y0 < 0 || x1 > panel.width || y1 > panel.height) {
      problems.push(problem("text-in-panel", "a line runs outside the panel"));
      break;
    }
  }
  const step = cap / 4;
  outer: for (const [x0, y0, x1, y1] of boxes) {
    for (let x = x0; x <= x1; x += step) {
      for (let y = y0; y <= y1; y += step) {
        if (!open([x, y])) {
          problems.push(problem("text-off-art", `text over the art at ${x.toFixed(0)},${y.toFixed(0)}`));
          break outer;
        }
      }
    }
  }
  for (const other of others) {
    if (!other.outline) continue;
    if (boxes.some(([x0, y0, x1, y1]) => inside(other.outline, [(x0 + x1) / 2, (y0 + y1) / 2]))) {
      problems.push(problem("balloons-apart", `${speech.who}'s text is inside ${other.who}'s balloon`));
    }
  }

  const aimed = (tail, what) => {
    const direction = [tail.tip[0] - tail.bend[0], tail.tip[1] - tail.bend[1]];
    const toSpeaker = [speaker[0] - tail.tip[0], speaker[1] - tail.tip[1]];
    const off = angleBetween(direction, toSpeaker);
    if (off > LIMITS.aim) problems.push(problem(`${what}-aim`, `points ${off.toFixed(0)}° away from the speaker`));
    // The open space from the tip towards the speaker, up to the art (their
    // head, usually) or the speaker themselves.
    const distance = Math.hypot(...toSpeaker);
    let run = 0;
    while (run < distance && open([tail.tip[0] + (toSpeaker[0] * run) / distance, tail.tip[1] + (toSpeaker[1] * run) / distance])) {
      run += cap / 4;
    }
    const reach = Math.min(run, distance) / cap;
    if (reach > LIMITS.reach) {
      problems.push(problem(`${what}-reach`, `ends ${reach.toFixed(1)} caps short of the speaker`));
    }
  };

  if (style === "loose") {
    if (!speech.stroke) problems.push(problem("stroke", "loose lettering has no pen stroke"));
    else aimed(speech.stroke, "stroke");
    return problems;
  }

  const { outline, tail } = speech;
  if (!outline) {
    problems.push(problem("balloon", "no balloon"));
    return problems;
  }
  const corners = boxes.flatMap(([x0, y0, x1, y1]) => [
    [x0, y0],
    [x1, y0],
    [x0, y1],
    [x1, y1],
  ]);
  if (!corners.every((p) => inside(outline, p))) {
    problems.push(problem("encloses", "some lettering is outside its balloon"));
  }
  // The outline as drawn: the stretches of it inside the panel (a balloon
  // hanging from the border leaves the panel and comes back).
  const stretches = [[]];
  for (const p of densify(outline, step / 2)) {
    if (p[0] >= 0 && p[0] <= panel.width && p[1] >= 0 && p[1] <= panel.height) {
      stretches[stretches.length - 1].push(p);
    } else if (stretches[stretches.length - 1].length) {
      stretches.push([]);
    }
  }
  const visible = stretches.flat();
  // (A loop: a big balloon has too many points to spread into Math.min.)
  let nearest = Infinity;
  for (const p of visible) for (const b of boxes) nearest = Math.min(nearest, distanceToBox(p, b));
  if (nearest / cap < LIMITS.clearance) {
    problems.push(problem("clearance", `the outline comes within ${(nearest / cap).toFixed(2)} caps of the lettering`));
  }
  const onArt = visible.filter((p) => !open(p)).length / Math.max(1, visible.length);
  if (onArt > LIMITS.outlineOnArt) {
    problems.push(problem("balloon-off-art", `${(onArt * 100).toFixed(0)}% of the outline is on the art`));
  }
  if (smoothness && visible.length > 2) {
    let sharpest = 0;
    for (const stretch of stretches) {
      if (stretch.length < 3) continue;
      const points = resample(stretch, step);
      for (let i = 1; i < points.length - 1; i++) {
        const a = points[i - 1];
        const b = points[i];
        const c = points[i + 1];
        sharpest = Math.max(sharpest, angleBetween([b[0] - a[0], b[1] - a[1]], [c[0] - b[0], c[1] - b[1]]));
      }
    }
    if (sharpest > LIMITS.turn) problems.push(problem("smooth", `the outline turns ${sharpest.toFixed(0)}° at once`));
  }
  if (!tail) {
    problems.push(problem("tail", "the balloon has no tail"));
  } else {
    aimed(tail, "tail");
    const base = [(tail.base[0][0] + tail.base[1][0]) / 2, (tail.base[0][1] + tail.base[1][1]) / 2];
    const length = Math.hypot(tail.tip[0] - base[0], tail.tip[1] - base[1]) / cap;
    if (length > LIMITS.tailLength && artWithin(base, LIMITS.tailLength * cap, step, open)) {
      problems.push(problem("tail-length", `a ${length.toFixed(1)} cap tail from a balloon right by the art`));
    }
    const tailPoints = [...tail.base, tail.bend, tail.tip];
    if (others.some((o) => o.outline && tailPoints.some((p) => inside(o.outline, p)))) {
      problems.push(problem("tail-clear", "the tail runs into another balloon"));
    }
  }
  return problems;
}

// Problems with a whole comic, as reported by drawComic: a list of
// {panel (its number from 1), who, check, detail}.
export function checkComic(report) {
  const problems = [];
  if (!report.fits) problems.push({ panel: 0, who: "", check: "fits", detail: "the text doesn't fit" });
  report.panels.forEach(({ panel, meta, speech, speeches }, i) => {
    for (const s of speeches) {
      const style = s.who === "calvin" ? "balloon" : speech;
      const found = checkSpeech(s, speeches.filter((o) => o !== s), {
        cap: report.cap,
        panel,
        // Outside the panel there's no art, only the border.
        open: ([x, y]) =>
          x < 0 || y < 0 || x > panel.width || y > panel.height || openAt(panel, meta, [x, y]),
        style,
        smoothness: true,
      });
      for (const p of found) problems.push({ panel: i + 1, who: s.who, ...p });
    }
  });
  return problems;
}
