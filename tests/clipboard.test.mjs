import { test } from "node:test";
import assert from "node:assert/strict";

import { dataUrlToBlob } from "../js/clipboard.js";

test("a data URL becomes a blob of the same bytes and type", async () => {
  const bytes = [137, 80, 78, 71, 0, 255];
  const url = "data:image/png;base64," + btoa(String.fromCharCode(...bytes));
  const blob = dataUrlToBlob(url);
  assert.equal(blob.type, "image/png");
  assert.deepEqual([...new Uint8Array(await blob.arrayBuffer())], bytes);
});
