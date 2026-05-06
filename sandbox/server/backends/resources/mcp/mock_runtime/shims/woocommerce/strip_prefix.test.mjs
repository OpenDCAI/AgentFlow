import assert from "node:assert/strict";
import test from "node:test";

import { stripWooPrefix } from "./strip_prefix.mjs";

test("strips the WooCommerce REST prefix from matching paths", () => {
  assert.equal(
    stripWooPrefix("/wp-json/wc/v3/orders/12"),
    "orders/12",
  );
});

test("rejects non-matching WooCommerce REST paths", () => {
  assert.throws(
    () => stripWooPrefix("/api/orders/12"),
    /WooCommerce REST prefix/,
  );
});
