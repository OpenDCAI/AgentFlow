import fs from "node:fs";
import assert from "node:assert/strict";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import * as serverModule from "./server.mjs";

test("path params override query params and body params", () => {
  const params = serverModule.__test__?.buildOperationParams(
    { database_id: "abc", user_id: "123" },
    { user_id: "456", filter: "active" },
    { database_id: "override", page_size: 10 },
  );

  assert.deepEqual(params, {
    database_id: "abc",
    filter: "active",
    page_size: 10,
    user_id: "123",
  });
});

test("internal server errors stay opaque to clients", async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "notion-shim-"));
  fs.mkdirSync(
    path.join(
      root,
      "local_servers/notion-mcp-server/scripts",
    ),
    { recursive: true },
  );
  fs.mkdirSync(
    path.join(
      root,
      "local_servers/notion-mcp-server/build/src/openapi-mcp-server/client",
    ),
    { recursive: true },
  );

  fs.writeFileSync(
    path.join(root, "package.json"),
    JSON.stringify({ type: "module" }),
  );
  fs.writeFileSync(
    path.join(
      root,
      "local_servers/notion-mcp-server/scripts/notion-openapi.json",
    ),
    JSON.stringify({ paths: { "/v1/test": { get: {} } } }),
  );
  fs.writeFileSync(
    path.join(
      root,
      "local_servers/notion-mcp-server/build/src/openapi-mcp-server/client/pg-client.js",
    ),
    "export class PgHttpClient { async executeOperation() { throw new Error('boom: secret detail'); } }\n",
  );

  const previousEnv = {
    TOOLATHLON_GYM_ROOT: process.env.TOOLATHLON_GYM_ROOT,
    NOTION_SHIM_HOST: process.env.NOTION_SHIM_HOST,
    NOTION_SHIM_PORT: process.env.NOTION_SHIM_PORT,
  };
  process.env.TOOLATHLON_GYM_ROOT = root;
  process.env.NOTION_SHIM_HOST = "127.0.0.1";
  process.env.NOTION_SHIM_PORT = "0";

  const consoleErrors = [];
  const originalConsoleError = console.error;
  console.error = (...args) => {
    consoleErrors.push(args);
  };

  let server;
  try {
    ({ server } = await serverModule.createNotionShimServer());

    await new Promise((resolve) => {
      server.listen(0, "127.0.0.1", resolve);
    });

    const address = server.address();
    assert.ok(address && typeof address !== "string");

    const response = await new Promise((resolve, reject) => {
      const req = http.request(
        {
          hostname: "127.0.0.1",
          port: address.port,
          path: "/v1/test",
          method: "GET",
        },
        (res) => {
          const chunks = [];
          res.on("data", (chunk) => chunks.push(chunk));
          res.on("end", () => {
            resolve({
              body: Buffer.concat(chunks).toString("utf8"),
              statusCode: res.statusCode,
            });
          });
        },
      );

      req.on("error", reject);
      req.end();
    });

    assert.equal(response.statusCode, 500);
    assert.deepEqual(JSON.parse(response.body), { error: "internal_error" });
    assert.equal(consoleErrors.length > 0, true);
    assert.match(String(consoleErrors[0][0]), /boom: secret detail/);
  } finally {
    console.error = originalConsoleError;
    process.env.TOOLATHLON_GYM_ROOT = previousEnv.TOOLATHLON_GYM_ROOT;
    process.env.NOTION_SHIM_HOST = previousEnv.NOTION_SHIM_HOST;
    process.env.NOTION_SHIM_PORT = previousEnv.NOTION_SHIM_PORT;
    await new Promise((resolve) => {
      server?.close(resolve);
    });
  }
});
