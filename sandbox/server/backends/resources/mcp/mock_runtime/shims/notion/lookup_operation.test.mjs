import assert from "node:assert/strict";
import test from "node:test";

import { lookupOperation } from "./lookup_operation.mjs";

const spec = {
  paths: {
    "/v1/users/{user_id}": {
      get: {
        operationId: "get-user",
      },
    },
    "/v1/users": {
      get: {
        operationId: "get-users",
      },
    },
    "/v1/users/me": {
      get: {
        operationId: "get-self",
      },
    },
    "/v1/databases/{database_id}/query": {
      post: {
        operationId: "post-database-query",
      },
    },
  },
};

test("prefers exact notion route matches over placeholder routes", () => {
  const match = lookupOperation(spec, "GET", "/v1/users/me");

  assert.deepEqual(match, {
    operation: {
      operationId: "get-self",
    },
    pathParams: {},
  });
});

test("matches notion placeholder routes and extracts path params", () => {
  const match = lookupOperation(spec, "POST", "/v1/databases/abc/query");

  assert.deepEqual(match, {
    operation: {
      operationId: "post-database-query",
    },
    pathParams: {
      database_id: "abc",
    },
  });
});

test("returns null when no notion operation matches the request", () => {
  assert.equal(lookupOperation(spec, "DELETE", "/v1/users/me"), null);
});
