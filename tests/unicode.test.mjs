import { test } from "node:test";
import assert from "node:assert/strict";
import { graphemes, graphemePrefix } from "../js/unicode.js";
import { layoutColumn } from "../js/layout.js";
import { readFileSync } from "node:fs";

test("Unicode 18 extended grapheme cluster conformance corpus", () => {
  const corpus = readFileSync(new URL("../data/unicode/18.0.0/auxiliary/GraphemeBreakTest.txt", import.meta.url), "utf8");
  let count = 0;
  for (const line of corpus.split("\n")) {
    const body = line.split("#")[0].trim();
    if (!body) continue;
    const expected = body.split("÷").map((s) => s.trim()).filter(Boolean)
      .map((s) => s.split(/\s+/).filter((t) => t !== "×").map((cp) => String.fromCodePoint(parseInt(cp, 16))).join(""));
    assert.deepEqual(graphemes(expected.join("")), expected, line);
    count++;
  }
  assert.ok(count > 500, `read ${count} cases`);
});

test("all pinned recommended emoji sequences remain single clusters", () => {
  for (const name of ["emoji-sequences.txt", "emoji-zwj-sequences.txt"]) {
    const corpus = readFileSync(new URL(`../data/unicode/18.0.0/emoji/${name}`, import.meta.url), "utf8");
    for (const line of corpus.split("\n")) {
      const body = line.split("#")[0].trim();
      if (!body) continue;
      const sequence = body.split(";")[0].trim();
      if (sequence.includes("..")) continue; // singleton ranges
      const text = sequence.split(/\s+/).map((cp) => String.fromCodePoint(parseInt(cp, 16))).join("");
      assert.equal(graphemes(text).length, 1, line);
    }
  }
});

test("emergency wrapping retains complete emoji, accents, and supplementary characters", () => {
  for (const unit of ["𓀀", "e\u0301", "👩🏽‍🚀", "🇫🇷", "क्‍ष", "A\u0301\u0334\u0323"]) {
    const text = unit.repeat(4);
    const result = layoutColumn(text, {
      measure: (s) => graphemes(s).length * 10,
      fontSize: 10, width: 15,
    });
    assert.deepEqual(result.lines.map((l) => l.text), [unit, unit, unit, unit]);
    assert.equal(result.lines.map((l) => l.text).join(""), text);
  }
});

test("length caps never cut into grapheme clusters", () => {
  for (const cluster of ["𓀀", "e\u0301", "👩🏽‍🚀", "🇫🇷"]) {
    const text = "ab" + cluster + "c";
    for (let cap = 2; cap < 2 + cluster.length; cap++) {
      assert.equal(graphemePrefix(text, cap), "ab");
    }
    assert.equal(graphemePrefix(text, 2 + cluster.length), "ab" + cluster);
  }
  assert.equal(graphemePrefix("x" + "\u0301".repeat(100), 50), "");
});

test('bounded prefix agrees with full segmentation at every cut, including lookahead', () => {
  for (const text of ['a\r\nb', '🇫🇷🇺🇸🇯🇵', 'x👩🏽‍🚀y', 'a\u0600b\u0301c', 'क्‍षक्‍ष', 'x\u0301\u0302y', 'a𞤀\u{1e944}z']) {
    for (let cap = 0; cap <= text.length + 1; cap++) {
      let expected = '';
      for (const cluster of graphemes(text)) {
        if (expected.length + cluster.length > cap) break;
        expected += cluster;
      }
      assert.equal(graphemePrefix(text, cap), expected, `${JSON.stringify(text)}, ${cap}`);
    }
  }
});

test('an oversized combining cluster is rejected without scanning the whole paste', () => {
  const text = 'abc X' + '\u0301'.repeat(2_000_000);
  const start = performance.now();
  assert.equal(graphemePrefix(text, 5000), 'abc ');
  assert.ok(performance.now() - start < 1000);
});

test('Tai Yo medial and rhyme marks stay with their consonant during wrapping',()=>{
  const cases=[
    [0x1e6c5,0x1e6ee,0x1e6ee],
    [0x1e6dc,0x1e6ee,0x1e6ef],
    ...[0x1e6cd,0x1e6d5].flatMap(base=>[0x1e6e3,0x1e6e6,0x1e6ee,0x1e6ef,0x1e6f5].map(mark=>[base,mark])),
  ];
  for(const points of cases){
    const unit=String.fromCodePoint(...points);
    assert.deepEqual(graphemes(unit),[unit]);
    const result=layoutColumn(unit.repeat(3),{
      measure:s=>graphemes(s).length*10,fontSize:10,width:15,
    });
    assert.deepEqual(result.lines.map(l=>l.text),[unit,unit,unit]);
  }
  const letterUE=String.fromCodePoint(0x1e6d1,0x1e6e2,0x1e6cf);
  const signUE=String.fromCodePoint(0x1e6d6,0x1e6e3);
  assert.equal(graphemes(letterUE).length,3);
  assert.equal(graphemes(signUE).length,1);
});
