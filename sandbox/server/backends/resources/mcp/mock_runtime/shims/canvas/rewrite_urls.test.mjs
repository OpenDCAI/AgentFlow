import assert from "node:assert/strict";
import test from "node:test";

import { rewriteCanvasPublicUrl } from "./rewrite_urls.mjs";

test("rewrites mock canvas upload URLs to the public shim base URL", () => {
  assert.equal(
    rewriteCanvasPublicUrl(
      "https://mock-canvas.local/upload/123",
      "https://127.0.0.1:38080",
    ),
    "https://127.0.0.1:38080/upload/123",
  );
});

test("leaves normal URLs unchanged", () => {
  const url = "https://example.com/upload/123?x=1";

  assert.equal(
    rewriteCanvasPublicUrl(url, "https://127.0.0.1:38080"),
    url,
  );
});
