import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { pathToFileURL } from "node:url";

import { lookupOperation } from "./lookup_operation.mjs";

function resolveToolathlonGymRoot() {
  const root = process.env.TOOLATHLON_GYM_ROOT;
  if (!root) {
    throw new Error("TOOLATHLON_GYM_ROOT is required");
  }

  return path.resolve(root);
}

function deriveClientEnv() {
  process.env.PG_HOST ||= "127.0.0.1";
  process.env.PG_PORT ||= process.env.POSTGRES_HOST_PORT || "5432";
  process.env.PG_DATABASE ||= process.env.POSTGRES_DB || "toolathlon_gym";
  process.env.PG_USER ||= process.env.POSTGRES_USER || "eigent";
  process.env.PG_PASSWORD ||= process.env.POSTGRES_PASSWORD || "camel";
}

function getServerOptions() {
  return {
    host: process.env.NOTION_SHIM_HOST || "127.0.0.1",
    port: Number(process.env.NOTION_SHIM_PORT || "38081"),
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
    return {};
  }

  try {
    const parsed = JSON.parse(rawBody);
    return parsed && typeof parsed === "object" && !Array.isArray(parsed)
      ? parsed
      : {};
  } catch (error) {
    if (error instanceof SyntaxError) {
      error.code = "invalid_json";
    }

    throw error;
  }
}

function buildOperationParams(pathParams, queryParams, bodyParams) {
  return {
    ...queryParams,
    ...bodyParams,
    ...pathParams,
  };
}

function extractResponsePayload(result) {
  if (result?.body !== undefined) {
    return result.body;
  }

  if (result?.data !== undefined) {
    return result.data;
  }

  return {};
}

function getOperationStatus(result) {
  return Number.isInteger(result?.status) ? result.status : 200;
}

function getOperationResponse(result) {
  return {
    payload: extractResponsePayload(result),
    status: getOperationStatus(result),
  };
}

function loadOpenApiSpec() {
  const gymRoot = resolveToolathlonGymRoot();
  const specPath = path.join(
    gymRoot,
    "local_servers/notion-mcp-server/scripts/notion-openapi.json",
  );

  if (!fs.existsSync(specPath)) {
    throw new Error(`Notion OpenAPI spec not found: ${specPath}`);
  }

  return JSON.parse(fs.readFileSync(specPath, "utf8"));
}

async function loadPgHttpClient() {
  const gymRoot = resolveToolathlonGymRoot();
  const clientModulePath = path.join(
    gymRoot,
    "local_servers/notion-mcp-server/build/src/openapi-mcp-server/client/pg-client.js",
  );

  if (!fs.existsSync(clientModulePath)) {
    throw new Error(`PgHttpClient build not found: ${clientModulePath}`);
  }

  const clientModule = await import(pathToFileURL(clientModulePath).href);
  const PgHttpClient = clientModule.PgHttpClient
    || clientModule.default?.PgHttpClient
    || clientModule.default;

  if (typeof PgHttpClient !== "function") {
    throw new Error(`PgHttpClient export missing: ${clientModulePath}`);
  }

  return PgHttpClient;
}

async function forwardToNotionClient(req, res, requestUrl, spec, client) {
  const match = lookupOperation(spec, req.method || "GET", requestUrl.pathname);

  if (!match) {
    sendJson(res, 404, { error: "not_found", path: requestUrl.pathname });
    return;
  }

  const bodyParams = ["POST", "PATCH", "PUT"].includes(req.method || "")
    ? await parseJsonBody(req)
    : {};
  const params = buildOperationParams(
    match.pathParams,
    collectQueryParams(requestUrl.searchParams),
    bodyParams,
  );
  const result = await client.executeOperation(match.operation, params);
  const response = getOperationResponse(result);

  sendJson(res, response.status, response.payload);
}

export async function createNotionShimServer() {
  deriveClientEnv();

  const [spec, PgHttpClient] = await Promise.all([
    loadOpenApiSpec(),
    loadPgHttpClient(),
  ]);
  const client = new PgHttpClient();
  const serverOptions = getServerOptions();
  const baseUrl = `http://${serverOptions.host}:${serverOptions.port}`;

  const server = http.createServer(async (req, res) => {
    try {
      const requestUrl = new URL(req.url || "/", baseUrl);

      if (req.method === "GET" && requestUrl.pathname === "/healthz") {
        sendJson(res, 200, { ok: true });
        return;
      }

      if (requestUrl.pathname.startsWith("/v1/")) {
        await forwardToNotionClient(req, res, requestUrl, spec, client);
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
    client,
    host: serverOptions.host,
    port: serverOptions.port,
    server,
  };
}

export async function startNotionShimServer() {
  const { server, client, host, port } = await createNotionShimServer();

  await new Promise((resolve) => {
    server.listen(port, host, resolve);
  });

  return { client, server };
}

export const __test__ = {
  buildOperationParams,
};

async function shutdown(server, client, code = 0) {
  server.close(() => {
    Promise.resolve(client.pool?.end?.())
      .finally(() => {
        process.exit(code);
      });
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const { server, client } = await startNotionShimServer();
    const address = server.address();

    if (!address || typeof address === "string") {
      throw new Error("Notion shim failed to bind a TCP port");
    }

    console.log(`READY ${address.port}`);

    process.on("SIGTERM", () => {
      shutdown(server, client, 0);
    });
    process.on("SIGINT", () => {
      shutdown(server, client, 0);
    });
  } catch (error) {
    console.error(String(error));
    process.exit(1);
  }
}
