import fs from "node:fs";
import https from "node:https";
import path from "node:path";
import { pathToFileURL } from "node:url";

import { rewriteCanvasPublicUrl } from "./rewrite_urls.mjs";

function resolveToolathlonGymRoot() {
  const root = process.env.TOOLATHLON_GYM_ROOT;
  if (!root) {
    throw new Error("TOOLATHLON_GYM_ROOT is required");
  }

  return path.resolve(root);
}

function deriveRouterEnv() {
  process.env.PG_HOST ||= "127.0.0.1";
  process.env.PG_PORT ||= process.env.POSTGRES_HOST_PORT || "5432";
  process.env.PG_DATABASE ||= process.env.POSTGRES_DB || "toolathlon";
  process.env.PG_USER ||= process.env.POSTGRES_USER || "postgres";
  process.env.PG_PASSWORD ||= process.env.POSTGRES_PASSWORD || "postgres";
}

async function loadPgCanvasRouter() {
  const gymRoot = resolveToolathlonGymRoot();
  const routerModulePath = path.join(
    gymRoot,
    "local_servers/mcp-canvas-lms/build/pg-canvas-router.js",
  );

  if (!fs.existsSync(routerModulePath)) {
    throw new Error(`PgCanvasRouter build not found: ${routerModulePath}`);
  }

  const routerModule = await import(pathToFileURL(routerModulePath).href);
  if (!routerModule.PgCanvasRouter) {
    throw new Error(`PgCanvasRouter export missing: ${routerModulePath}`);
  }

  return routerModule.PgCanvasRouter;
}

function resolveRuntimePath(filePath) {
  return path.isAbsolute(filePath)
    ? filePath
    : path.resolve(process.cwd(), filePath);
}

function getPublicBaseUrl() {
  const host = process.env.CANVAS_SHIM_HOST || "127.0.0.1";
  const port = Number(process.env.CANVAS_SHIM_PORT || "38080");
  return `https://${host}:${port}`;
}

function getServerOptions() {
  const certPath = process.env.CANVAS_TLS_CERT_PATH;
  const keyPath = process.env.CANVAS_TLS_KEY_PATH;

  if (!certPath || !keyPath) {
    throw new Error("CANVAS_TLS_CERT_PATH and CANVAS_TLS_KEY_PATH are required");
  }

  return {
    host: process.env.CANVAS_SHIM_HOST || "127.0.0.1",
    port: Number(process.env.CANVAS_SHIM_PORT || "38080"),
    cert: fs.readFileSync(resolveRuntimePath(certPath)),
    key: fs.readFileSync(resolveRuntimePath(keyPath)),
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

  return Buffer.concat(chunks);
}

async function drainRequestBody(req) {
  for await (const _chunk of req) {
    // Drain upload bodies without buffering them in memory.
  }
}

async function parseRouterBody(req) {
  const bodyBuffer = await readRequestBody(req);
  if (bodyBuffer.length === 0) {
    return {};
  }

  const contentType = req.headers["content-type"] || "";
  const rawBody = bodyBuffer.toString("utf8");

  if (contentType.includes("application/json")) {
    return JSON.parse(rawBody);
  }

  if (contentType.includes("application/x-www-form-urlencoded")) {
    return Object.fromEntries(new URLSearchParams(rawBody));
  }

  try {
    return JSON.parse(rawBody);
  } catch {
    return {};
  }
}

function rewriteCanvasPayload(value, publicBaseUrl) {
  if (Array.isArray(value)) {
    return value.map((item) => rewriteCanvasPayload(item, publicBaseUrl));
  }

  if (!value || typeof value !== "object") {
    return value;
  }

  const rewritten = {};

  for (const [key, nestedValue] of Object.entries(value)) {
    if (
      (key === "upload_url" || key === "location" || key === "url")
      && typeof nestedValue === "string"
    ) {
      rewritten[key] = rewriteCanvasPublicUrl(nestedValue, publicBaseUrl);
      continue;
    }

    rewritten[key] = rewriteCanvasPayload(nestedValue, publicBaseUrl);
  }

  return rewritten;
}

function rememberUploadMapping(payload, publicBaseUrl, uploadMappings) {
  if (
    !payload
    || typeof payload !== "object"
    || Array.isArray(payload)
    || payload.id === undefined
    || typeof payload.upload_url !== "string"
  ) {
    return;
  }

  const uploadUrl = new URL(
    rewriteCanvasPublicUrl(payload.upload_url, publicBaseUrl),
  );

  uploadMappings.set(uploadUrl.pathname, String(payload.id));
}

function rememberFileMapping(payload, publicBaseUrl, fileMappings) {
  if (
    !payload
    || typeof payload !== "object"
    || Array.isArray(payload)
    || payload.id === undefined
    || typeof payload.url !== "string"
  ) {
    return;
  }

  const fileUrl = new URL(
    rewriteCanvasPublicUrl(payload.url, publicBaseUrl),
  );
  const publicOrigin = new URL(publicBaseUrl).origin;

  if (
    fileUrl.origin !== publicOrigin
    || !fileUrl.pathname.startsWith("/files/")
  ) {
    return;
  }

  fileMappings.set(fileUrl.pathname, String(payload.id));
}

async function forwardToCanvasRouter(
  req,
  res,
  requestUrl,
  router,
  publicBaseUrl,
  uploadMappings,
  fileMappings,
) {
  const canvasPath = requestUrl.pathname.replace(/^\/api\/v1\/?/, "");
  const queryParams = collectQueryParams(requestUrl.searchParams);
  const method = req.method || "GET";

  let routerResponse;

  if (method === "GET") {
    routerResponse = await router.get(canvasPath, { params: queryParams });
  } else if (method === "POST") {
    routerResponse = await router.post(
      canvasPath,
      await parseRouterBody(req),
      { params: queryParams },
    );
  } else if (method === "PUT") {
    routerResponse = await router.put(
      canvasPath,
      await parseRouterBody(req),
      { params: queryParams },
    );
  } else if (method === "DELETE") {
    routerResponse = await router.delete(canvasPath, {
      data: await parseRouterBody(req),
      params: queryParams,
    });
  } else {
    sendJson(res, 405, { error: "method_not_allowed", method });
    return;
  }

  const payload = rewriteCanvasPayload(routerResponse.data, publicBaseUrl);
  rememberUploadMapping(payload, publicBaseUrl, uploadMappings);
  rememberFileMapping(payload, publicBaseUrl, fileMappings);
  sendJson(res, routerResponse.status || 200, payload);
}

async function handleUploadRequest(req, res, requestUrl, publicBaseUrl, uploadMappings) {
  if (req.method !== "POST") {
    sendJson(res, 405, { error: "method_not_allowed", method: req.method });
    return;
  }

  const fileId = uploadMappings.get(requestUrl.pathname);
  if (!fileId) {
    sendJson(res, 404, { error: "upload_not_found", path: requestUrl.pathname });
    return;
  }

  await drainRequestBody(req);

  sendJson(res, 200, {
    location: new URL(`/api/v1/files/${fileId}`, publicBaseUrl).toString(),
  });
}

async function handleFileRequest(req, res, requestUrl, router, publicBaseUrl, fileMappings) {
  if (req.method !== "GET") {
    sendJson(res, 405, { error: "method_not_allowed", method: req.method });
    return;
  }

  const fileId = fileMappings.get(requestUrl.pathname);
  if (!fileId) {
    sendJson(res, 404, { error: "file_not_found", path: requestUrl.pathname });
    return;
  }

  const routerResponse = await router.get(`files/${fileId}`, {
    params: collectQueryParams(requestUrl.searchParams),
  });
  const payload = rewriteCanvasPayload(routerResponse.data, publicBaseUrl);
  rememberFileMapping(payload, publicBaseUrl, fileMappings);
  sendJson(res, routerResponse.status || 200, payload);
}

export async function createCanvasShimServer() {
  deriveRouterEnv();

  const PgCanvasRouter = await loadPgCanvasRouter();
  const router = new PgCanvasRouter();
  const uploadMappings = new Map();
  const fileMappings = new Map();
  const publicBaseUrl = getPublicBaseUrl();
  const serverOptions = getServerOptions();

  const server = https.createServer(serverOptions, async (req, res) => {
    try {
      const requestUrl = new URL(req.url || "/", publicBaseUrl);

      if (req.method === "GET" && requestUrl.pathname === "/healthz") {
        sendJson(res, 200, { ok: true });
        return;
      }

      if (requestUrl.pathname.startsWith("/upload/")) {
        await handleUploadRequest(
          req,
          res,
          requestUrl,
          publicBaseUrl,
          uploadMappings,
        );
        return;
      }

      if (requestUrl.pathname.startsWith("/files/")) {
        await handleFileRequest(
          req,
          res,
          requestUrl,
          router,
          publicBaseUrl,
          fileMappings,
        );
        return;
      }

      if (requestUrl.pathname.startsWith("/api/v1/")) {
        await forwardToCanvasRouter(
          req,
          res,
          requestUrl,
          router,
          publicBaseUrl,
          uploadMappings,
          fileMappings,
        );
        return;
      }

      sendJson(res, 404, { error: "not_found", path: requestUrl.pathname });
    } catch (error) {
      sendJson(res, 500, { error: String(error) });
    }
  });

  return { server, router, host: serverOptions.host, port: serverOptions.port };
}

export const __test__ = {
  drainRequestBody,
  handleFileRequest,
};

export async function startCanvasShimServer() {
  const { server, router, host, port } = await createCanvasShimServer();

  await new Promise((resolve) => {
    server.listen(port, host, resolve);
  });

  return { server, router };
}

async function shutdown(server, router, code = 0) {
  server.close(() => {
    router.pool?.end?.().finally(() => {
      process.exit(code);
    });
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const { server, router } = await startCanvasShimServer();
    const address = server.address();

    if (!address || typeof address === "string") {
      throw new Error("Canvas shim failed to bind a TCP port");
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
