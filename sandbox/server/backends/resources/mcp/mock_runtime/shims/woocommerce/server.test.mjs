import assert from "node:assert/strict";
import { EventEmitter } from "node:events";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import * as serverModule from "./server.mjs";

function createGymRoot(routerSource) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "woocommerce-shim-"));

  fs.mkdirSync(
    path.join(
      root,
      "local_servers/woocommerce-mcp/dist/services",
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
      "local_servers/woocommerce-mcp/dist/services/pg-rest-router.js",
    ),
    routerSource,
  );

  return root;
}

async function makeRequest(port, { body, method, path: requestPath }) {
  return await new Promise((resolve, reject) => {
    const req = http.request(
      {
        hostname: "127.0.0.1",
        port,
        path: requestPath,
        method,
        headers: body
          ? {
            "content-type": "application/json",
            "content-length": Buffer.byteLength(body),
          }
          : undefined,
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

    if (body) {
      req.write(body);
    }

    req.end();
  });
}

async function startServerWithEnv(root) {
  const previousEnv = {
    TOOLATHLON_GYM_ROOT: process.env.TOOLATHLON_GYM_ROOT,
    WOOCOMMERCE_SHIM_HOST: process.env.WOOCOMMERCE_SHIM_HOST,
    WOOCOMMERCE_SHIM_PORT: process.env.WOOCOMMERCE_SHIM_PORT,
  };

  const restoreEnv = () => {
    for (const [key, value] of Object.entries(previousEnv)) {
      if (value === undefined) {
        delete process.env[key];
        continue;
      }

      process.env[key] = value;
    }
  };

  process.env.TOOLATHLON_GYM_ROOT = root;
  process.env.WOOCOMMERCE_SHIM_HOST = "127.0.0.1";
  process.env.WOOCOMMERCE_SHIM_PORT = "0";

  let server;
  try {
    ({ server } = await serverModule.createWooCommerceShimServer());

    await new Promise((resolve) => {
      server.listen(0, "127.0.0.1", resolve);
    });

    const address = server.address();
    assert.ok(address && typeof address !== "string");

    return {
      port: address.port,
      restore() {
        restoreEnv();
      },
      server,
    };
  } catch (error) {
    restoreEnv();
    await new Promise((resolve) => {
      server?.close(resolve);
    });
    throw error;
  }
}

function withEnv(overrides) {
  const previousEnv = {};

  for (const [key, value] of Object.entries(overrides)) {
    previousEnv[key] = process.env[key];

    if (value === undefined) {
      delete process.env[key];
      continue;
    }

    process.env[key] = value;
  }

  return () => {
    for (const [key, value] of Object.entries(previousEnv)) {
      if (value === undefined) {
        delete process.env[key];
        continue;
      }

      process.env[key] = value;
    }
  };
}

test("forwards WooCommerce POST requests to the router", async () => {
  const root = createGymRoot(`
    export class PgRestRouter {
      async post(path, data, options) {
        return {
          status: 201,
          data: { data, options, path },
        };
      }
    }
  `);

  const runtime = await startServerWithEnv(root);

  try {
    const response = await makeRequest(runtime.port, {
      method: "POST",
      path: "/wp-json/wc/v3/orders?status=pending&status=paid",
      body: JSON.stringify({ id: 42 }),
    });

    assert.equal(response.statusCode, 201);
    assert.deepEqual(JSON.parse(response.body), {
      data: { id: 42 },
      options: { params: { status: ["pending", "paid"] } },
      path: "orders",
    });
  } finally {
    runtime.restore();
    await new Promise((resolve) => {
      runtime.server.close(resolve);
    });
  }
});

test("rejects malformed WooCommerce JSON payloads with 400", async () => {
  const root = createGymRoot(`
    export class PgRestRouter {
      async post() {
        return {
          status: 201,
          data: { ok: true },
        };
      }
    }
  `);

  const runtime = await startServerWithEnv(root);

  try {
    const response = await makeRequest(runtime.port, {
      method: "POST",
      path: "/wp-json/wc/v3/orders",
      body: "{",
    });

    assert.equal(response.statusCode, 400);
    assert.deepEqual(JSON.parse(response.body), { error: "invalid_json" });
  } finally {
    runtime.restore();
    await new Promise((resolve) => {
      runtime.server.close(resolve);
    });
  }
});

test("maps downstream SyntaxError failures to opaque 500 responses", async () => {
  const root = createGymRoot(`
    export class PgRestRouter {
      async get() {
        throw new SyntaxError("boom: secret detail");
      }
    }
  `);

  const runtime = await startServerWithEnv(root);
  const consoleErrors = [];
  const originalConsoleError = console.error;
  console.error = (...args) => {
    consoleErrors.push(args);
  };

  try {
    const response = await makeRequest(runtime.port, {
      method: "GET",
      path: "/wp-json/wc/v3/orders",
    });

    assert.equal(response.statusCode, 500);
    assert.deepEqual(JSON.parse(response.body), { error: "internal_error" });
    assert.equal(consoleErrors.length > 0, true);
    assert.match(String(consoleErrors[0][0]), /boom: secret detail/);
  } finally {
    console.error = originalConsoleError;
    runtime.restore();
    await new Promise((resolve) => {
      runtime.server.close(resolve);
    });
  }
});

test("rejects when the shim server fails to bind", async () => {
  const root = createGymRoot(`
    globalThis.__wooCleanupStats = { endCalls: 0 };

    export class PgRestRouter {
      constructor() {
        this.pool = {
          end: async () => {
            globalThis.__wooCleanupStats.endCalls += 1;
          },
        };
      }
    }
  `);
  const restoreEnv = withEnv({
    TOOLATHLON_GYM_ROOT: root,
    WOOCOMMERCE_SHIM_HOST: "127.0.0.1",
    WOOCOMMERCE_SHIM_PORT: "38082",
  });
  const originalCreateServer = http.createServer;
  let closed = 0;

  http.createServer = () => {
    const server = new EventEmitter();
    server.close = (callback) => {
      closed += 1;
      callback?.();
    };
    server.listen = () => {
      process.nextTick(() => {
        if (server.listenerCount("error") > 0) {
          const error = new Error("bind failed");
          error.code = "EADDRINUSE";
          server.emit("error", error);
        }
      });
      return server;
    };
    return server;
  };

  try {
    const startPromise = Promise.race([
      serverModule.startWooCommerceShimServer(),
      new Promise((_, reject) => {
        setTimeout(() => {
          reject(new Error("timed out waiting for start failure"));
        }, 200);
      }),
    ]);

    await assert.rejects(startPromise, { code: "EADDRINUSE" });
    await assert.rejects(startPromise, { code: "EADDRINUSE" });
  } finally {
    http.createServer = originalCreateServer;
    restoreEnv();
  }

  assert.equal(closed, 1);
  assert.equal(globalThis.__wooCleanupStats.endCalls, 1);
  delete globalThis.__wooCleanupStats;
});

test("does not leak derived PG env across repeated server creation", async () => {
  const restoreEnv = withEnv({
    PG_HOST: undefined,
    PG_PORT: undefined,
    PG_DATABASE: undefined,
    PG_USER: undefined,
    PG_PASSWORD: undefined,
    WOOCOMMERCE_SHIM_HOST: "127.0.0.1",
    WOOCOMMERCE_SHIM_PORT: "0",
  });

  try {
    const root = createGymRoot(`
      export class PgRestRouter {
        constructor() {
          this.snapshot = {
            host: process.env.PG_HOST,
            port: process.env.PG_PORT,
            database: process.env.PG_DATABASE,
            user: process.env.PG_USER,
            password: process.env.PG_PASSWORD,
          };
        }
      }
    `);
    let firstRuntime;
    const restoreFirstEnv = withEnv({
      TOOLATHLON_GYM_ROOT: root,
      POSTGRES_HOST_PORT: "15432",
      POSTGRES_DB: "first_db",
      POSTGRES_USER: "first_user",
      POSTGRES_PASSWORD: "first_password",
      PG_USER: "explicit_first_user",
    });
    try {
      firstRuntime = await serverModule.createWooCommerceShimServer();
    } finally {
      restoreFirstEnv();
    }

    let secondRuntime;
    const restoreSecondEnv = withEnv({
      TOOLATHLON_GYM_ROOT: root,
      POSTGRES_HOST_PORT: "25432",
      POSTGRES_DB: "second_db",
      POSTGRES_USER: "second_user",
      POSTGRES_PASSWORD: "second_password",
    });
    try {
      secondRuntime = await serverModule.createWooCommerceShimServer();
    } finally {
      restoreSecondEnv();
    }

    assert.deepEqual(firstRuntime.router.snapshot, {
      host: "127.0.0.1",
      port: "15432",
      database: "first_db",
      user: "explicit_first_user",
      password: "first_password",
    });
    assert.deepEqual(secondRuntime.router.snapshot, {
      host: "127.0.0.1",
      port: "25432",
      database: "second_db",
      user: "second_user",
      password: "second_password",
    });
    assert.equal(process.env.PG_PORT, undefined);
    assert.equal(process.env.PG_USER, undefined);
  } finally {
    restoreEnv();
  }
});

test("serves /healthz without touching the router", async () => {
  const root = createGymRoot(`
    export class PgRestRouter {
      async get() {
        throw new Error("router should not be called");
      }
    }
  `);

  const runtime = await startServerWithEnv(root);

  try {
    const response = await makeRequest(runtime.port, {
      method: "GET",
      path: "/healthz",
    });

    assert.equal(response.statusCode, 200);
    assert.deepEqual(JSON.parse(response.body), { ok: true });
  } finally {
    runtime.restore();
    await new Promise((resolve) => {
      runtime.server.close(resolve);
    });
  }
});
