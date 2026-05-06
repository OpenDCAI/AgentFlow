import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { pathToFileURL } from "node:url";

import { stripWooPrefix } from "./strip_prefix.mjs";

function resolveToolathlonGymRoot() {
  const root = process.env.TOOLATHLON_GYM_ROOT;
  if (!root) {
    throw new Error("TOOLATHLON_GYM_ROOT is required");
  }

  return path.resolve(root);
}

function deriveRouterEnv() {
  return {
    PG_HOST: process.env.PG_HOST || "127.0.0.1",
    PG_PORT: process.env.PG_PORT || process.env.POSTGRES_HOST_PORT || "5432",
    PG_DATABASE: process.env.PG_DATABASE || process.env.POSTGRES_DB || "toolathlon_gym",
    PG_USER: process.env.PG_USER || process.env.POSTGRES_USER || "eigent",
    PG_PASSWORD: process.env.PG_PASSWORD || process.env.POSTGRES_PASSWORD || "camel",
  };
}

async function withRouterEnv(callback) {
  const derivedEnv = deriveRouterEnv();
  const previousEnv = {};

  for (const [key, value] of Object.entries(derivedEnv)) {
    previousEnv[key] = process.env[key];
    process.env[key] = value;
  }

  try {
    return await callback();
  } finally {
    for (const [key, value] of Object.entries(previousEnv)) {
      if (value === undefined) {
        delete process.env[key];
        continue;
      }

      process.env[key] = value;
    }
  }
}

async function loadPgRestRouter() {
  const gymRoot = resolveToolathlonGymRoot();
  const routerModulePath = path.join(
    gymRoot,
    "local_servers/woocommerce-mcp/dist/services/pg-rest-router.js",
  );

  if (!fs.existsSync(routerModulePath)) {
    throw new Error(`PgRestRouter build not found: ${routerModulePath}`);
  }

  const routerModule = await import(pathToFileURL(routerModulePath).href);
  const PgRestRouter = routerModule.PgRestRouter
    || routerModule.default?.PgRestRouter
    || routerModule.default;

  if (typeof PgRestRouter !== "function") {
    throw new Error(`PgRestRouter export missing: ${routerModulePath}`);
  }

  return PgRestRouter;
}

function getServerOptions() {
  return {
    host: process.env.WOOCOMMERCE_SHIM_HOST || "127.0.0.1",
    port: Number(process.env.WOOCOMMERCE_SHIM_PORT || "38082"),
  };
}

function sendJson(res, statusCode, payload) {
  res.writeHead(statusCode, { "content-type": "application/json" });
  res.end(JSON.stringify(payload));
}

function collectQueryParams(searchParams) {
  const params = {};

  for (const [key, value] of searchParams) {
    if (params[key] === undefined) {
      params[key] = value;
      continue;
    }

    params[key] = Array.isArray(params[key])
      ? [...params[key], value]
      : [params[key], value];
  }

  return params;
}

async function readRequestBody(req) {
  const chunks = [];

  for await (const chunk of req) {
    chunks.push(chunk);
  }

  return Buffer.concat(chunks).toString("utf8");
}

async function parseJsonBody(req) {
  const rawBody = await readRequestBody(req);
  if (!rawBody) {
    return undefined;
  }

  try {
    return JSON.parse(rawBody);
  } catch (error) {
    if (error instanceof SyntaxError) {
      error.code = "invalid_json";
    }

    throw error;
  }
}

async function forwardToWooRouter(req, res, requestUrl, router) {
  const method = req.method || "GET";
  const routerPath = stripWooPrefix(requestUrl.pathname);
  const params = collectQueryParams(requestUrl.searchParams);

  let routerResponse;

  if (method === "GET") {
    routerResponse = await router.get(routerPath, { params });
  } else if (method === "POST") {
    routerResponse = await router.post(
      routerPath,
      await parseJsonBody(req),
      { params },
    );
  } else if (method === "PUT") {
    routerResponse = await router.put(
      routerPath,
      await parseJsonBody(req),
      { params },
    );
  } else if (method === "DELETE") {
    const data = await parseJsonBody(req);
    const config = { params };

    if (data !== undefined) {
      config.data = data;
    }

    routerResponse = await router.delete(routerPath, config);
  } else {
    sendJson(res, 405, { error: "method_not_allowed", method });
    return;
  }

  sendJson(res, routerResponse.status || 200, routerResponse.data);
}

export async function createWooCommerceShimServer() {
  const { router } = await withRouterEnv(async () => {
    const LoadedPgRestRouter = await loadPgRestRouter();
    return {
      router: new LoadedPgRestRouter(),
    };
  });
  const serverOptions = getServerOptions();
  const baseUrl = `http://${serverOptions.host}:${serverOptions.port}`;

  const server = http.createServer(async (req, res) => {
    try {
      const requestUrl = new URL(req.url || "/", baseUrl);

      if (req.method === "GET" && requestUrl.pathname === "/healthz") {
        sendJson(res, 200, { ok: true });
        return;
      }

      if (requestUrl.pathname.startsWith("/wp-json/wc/v3/")) {
        await forwardToWooRouter(req, res, requestUrl, router);
        return;
      }

      sendJson(res, 404, { error: "not_found", path: requestUrl.pathname });
    } catch (error) {
      if (error instanceof SyntaxError && error.code === "invalid_json") {
        sendJson(res, 400, { error: "invalid_json" });
        return;
      }

      console.error(error);
      sendJson(res, 500, { error: "internal_error" });
    }
  });

  return {
    host: serverOptions.host,
    port: serverOptions.port,
    router,
    server,
  };
}

async function cleanupStartFailure(server, router) {
  await new Promise((resolve) => {
    try {
      server.close(() => {
        resolve();
      });
    } catch {
      resolve();
    }
  });

  try {
    await router.pool?.end?.();
  } catch {
    // Best-effort cleanup for startup failures.
  }
}

export async function startWooCommerceShimServer() {
  const { server, router, host, port } = await createWooCommerceShimServer();

  await new Promise((resolve, reject) => {
    const rejectWithCleanup = (error) => {
      server.off("listening", handleListening);
      server.off("error", handleError);
      cleanupStartFailure(server, router).finally(() => {
        reject(error);
      });
    };
    const handleError = (error) => {
      rejectWithCleanup(error);
    };
    const handleListening = () => {
      server.off("error", handleError);
      resolve();
    };

    server.once("error", handleError);
    server.once("listening", handleListening);

    try {
      server.listen(port, host);
    } catch (error) {
      server.off("error", handleError);
      server.off("listening", handleListening);
      cleanupStartFailure(server, router).finally(() => {
        reject(error);
      });
    }
  });

  return { router, server };
}

async function shutdown(server, router, code = 0) {
  server.close(() => {
    Promise.resolve(router.pool?.end?.())
      .finally(() => {
        process.exit(code);
      });
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const { server, router } = await startWooCommerceShimServer();
    const address = server.address();

    if (!address || typeof address === "string") {
      throw new Error("WooCommerce shim failed to bind a TCP port");
    }

    console.log(`READY ${address.port}`);

    process.on("SIGTERM", () => {
      shutdown(server, router, 0);
    });
    process.on("SIGINT", () => {
      shutdown(server, router, 0);
    });
  } catch (error) {
    console.error(String(error));
    process.exit(1);
  }
}
