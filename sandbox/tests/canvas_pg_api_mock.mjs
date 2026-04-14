import fs from "fs";
import https from "https";
import { createRequire } from "module";

const requireFrom = process.env.CANVAS_MOCK_REQUIRE_FROM;
if (!requireFrom) {
  throw new Error("CANVAS_MOCK_REQUIRE_FROM is required");
}

const certPath = process.env.CANVAS_MOCK_TLS_CERT;
const keyPath = process.env.CANVAS_MOCK_TLS_KEY;
if (!certPath || !keyPath) {
  throw new Error("CANVAS_MOCK_TLS_CERT and CANVAS_MOCK_TLS_KEY are required");
}

const host = process.env.CANVAS_MOCK_HOST || "127.0.0.1";
const port = Number(process.env.CANVAS_MOCK_PORT || "0");

const require = createRequire(requireFrom);
const { Pool } = require("pg");

const pool = new Pool({
  host: process.env.PGHOST || process.env.PG_HOST || "127.0.0.1",
  port: Number(process.env.PGPORT || process.env.PG_PORT || "5432"),
  user: process.env.PGUSER || process.env.PG_USER || "postgres",
  password: process.env.PGPASSWORD || process.env.PG_PASSWORD || "postgres",
  database: process.env.PGDATABASE || process.env.PG_DATABASE || "toolathlon",
});

function sendJson(res, statusCode, payload) {
  res.writeHead(statusCode, { "content-type": "application/json" });
  res.end(JSON.stringify(payload));
}

const server = https.createServer(
  {
    cert: fs.readFileSync(certPath),
    key: fs.readFileSync(keyPath),
  },
  async (req, res) => {
    try {
      const url = new URL(req.url, `https://${host}`);

      if (req.method === "GET" && url.pathname === "/api/v1/courses") {
        const result = await pool.query(
          `
          SELECT *
          FROM canvas.courses
          ORDER BY id
          `
        );
        sendJson(res, 200, result.rows);
        return;
      }

      if (req.method === "GET" && url.pathname === "/api/v1/users/self/profile") {
        const result = await pool.query(
          `
          SELECT *
          FROM canvas.users
          ORDER BY id
          LIMIT 1
          `
        );
        sendJson(res, 200, result.rows[0] || {});
        return;
      }

      sendJson(res, 404, { error: "not_found", path: url.pathname });
    } catch (error) {
      sendJson(res, 500, { error: String(error) });
    }
  }
);

function shutdown(code = 0) {
  server.close(() => {
    pool.end().finally(() => process.exit(code));
  });
}

process.on("SIGTERM", () => shutdown(0));
process.on("SIGINT", () => shutdown(0));

server.listen(port, host, () => {
  const address = server.address();
  if (!address || typeof address === "string") {
    throw new Error("Canvas mock failed to bind a TCP port");
  }
  console.log(`READY ${address.port}`);
});
