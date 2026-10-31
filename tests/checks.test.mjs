import { test } from "node:test";
import assert from "node:assert/strict";

import { checkSpeech } from "../js/checks.js";

const cap = 10;
const open = () => true;
const panel = { width: 400, height: 400 };

// A line of text 100 wide, 16 tall (a 10px cap in the middle), at (100, 100).
const line = { x: 100, y: 100, width: 100, height: 16 };

function box(x0, y0, x1, y1) {
  return [
    [x0, y0],
    [x1, y0],
    [x1, y1],
    [x0, y1],
  ];
}

// A balloon padded well round the line, with a tail pointing down at a
// speaker below it.
const good = {
  who: "dad",
  lines: [line],
  speaker: [150, 200],
  outline: box(90, 90, 210, 126),
  tail: { base: [[145, 126], [155, 126]], bend: [150, 135], tip: [150, 145] },
};

const names = (problems) => problems.map((p) => p.check);

test("a well made balloon passes", () => {
  assert.deepEqual(checkSpeech(good, [], { cap, panel, open, style: "balloon" }), []);
});

test("text outside its balloon is caught", () => {
  const speech = { ...good, outline: box(120, 90, 210, 126) };
  assert.ok(names(checkSpeech(speech, [], { cap, panel, open, style: "balloon" })).includes("encloses"));
});

test("an outline crowding the text is caught", () => {
  const speech = { ...good, outline: box(99, 99, 201, 117) };
  assert.ok(names(checkSpeech(speech, [], { cap, panel, open, style: "balloon" })).includes("clearance"));
});

test("a missing tail is caught", () => {
  const speech = { ...good, tail: null };
  assert.ok(names(checkSpeech(speech, [], { cap, panel, open, style: "balloon" })).includes("tail"));
});

test("a tail pointing away from the speaker is caught", () => {
  const speech = {
    ...good,
    tail: { base: [[145, 126], [155, 126]], bend: [165, 135], tip: [180, 145] },
    speaker: [60, 200],
  };
  assert.ok(names(checkSpeech(speech, [], { cap, panel, open, style: "balloon" })).includes("tail-aim"));
});

test("a balloon stranded far from its speaker is caught", () => {
  const speech = { ...good, speaker: [150, 390] };
  assert.ok(
    names(checkSpeech(speech, [], { cap, panel, open, style: "balloon" })).includes("tail-reach"),
  );
});

test("text over the art is caught", () => {
  const art = ([x, y]) => !(x > 150 && x < 160 && y > 100 && y < 116);
  assert.ok(
    names(checkSpeech(good, [], { cap, panel, open: art, style: "balloon" })).includes("text-off-art"),
  );
});

test("a sharp corner in the outline is caught", () => {
  // The square outline has four right angles.
  assert.ok(
    names(checkSpeech(good, [], { cap, panel, open, style: "balloon", smoothness: true })).includes("smooth"),
  );
});

test("a tail running into another balloon is caught", () => {
  const other = { who: "calvin", lines: [], outline: box(140, 130, 220, 200) };
  assert.ok(
    names(checkSpeech(good, [other], { cap, panel, open, style: "balloon" })).includes("tail-clear"),
  );
});

test("loose lettering needs its stroke", () => {
  const speech = { ...good, outline: undefined, tail: undefined, stroke: null };
  assert.ok(names(checkSpeech(speech, [], { cap, panel, open, style: "loose" })).includes("stroke"));
});

test("a tail ending just short of the speaker's head is near enough, however far the mouth", () => {
  // The speaker's head starts 10px below the tip; the mouth is 25 caps on.
  const head = ([, y]) => y < 155;
  const speech = { ...good, speaker: [150, 400] };
  assert.ok(!names(checkSpeech(speech, [], { cap, panel, open: head, style: "balloon" })).includes("tail-reach"));
});

test("a long tail from a balloon that is already beside the speaker is caught", () => {
  // The speaker's head is just below the balloon, but the tail runs on 8
  // caps past it, down to their mouth.
  const head = ([x, y]) => !(x > 120 && x < 190 && y > 140);
  const speech = {
    ...good,
    speaker: [180, 220],
    tail: { base: [[195, 126], [205, 126]], bend: [200, 170], tip: [200, 215] },
  };
  assert.ok(names(checkSpeech(speech, [], { cap, panel, open: head, style: "balloon" })).includes("tail-length"));
  // An ordinary tail there is fine.
  assert.ok(!names(checkSpeech(good, [], { cap, panel, open: head, style: "balloon" })).includes("tail-length"));
});

test("how far a tail ends from its speaker is judged at the art's scale, not the lettering's", () => {
  // The lettering is half its usual size: the tail ends 8 of its caps (4 of
  // the art's) above the speaker.
  const speech = { ...good, speaker: [150, 225] };
  const small = { cap, panel, open, style: "balloon" };
  assert.ok(names(checkSpeech(speech, [], small)).includes("tail-reach"));
  assert.ok(!names(checkSpeech(speech, [], { ...small, artCap: 2 * cap })).includes("tail-reach"));
});
