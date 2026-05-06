import assert from "node:assert/strict";
import { Readable } from "node:stream";
import test from "node:test";

import { __test__ } from "./server.mjs";

function createMockResponse() {
  return {
    body: "",
    headers: undefined,
    statusCode: undefined,
    end(chunk = "") {
      this.body = String(chunk);
    },
    writeHead(statusCode, headers) {
      this.statusCode = statusCode;
      this.headers = headers;
    },
  };
}

test("bridges rewritten file URLs to the router GET files/:id endpoint", async () => {
  const response = createMockResponse();
  const routerCalls = [];
  const fileMappings = new Map([["/files/report.pdf", "file-42"]]);
  const publicBaseUrl = "https://127.0.0.1:38080";

  await __test__.handleFileRequest(
    { method: "GET" },
    response,
    new URL("/files/report.pdf", publicBaseUrl),
    {
      async get(path, options) {
        routerCalls.push({ path, options });
        return {
          status: 200,
          data: {
            id: "file-42",
            url: "https://mock-canvas.local/files/report.pdf",
          },
        };
      },
    },
    publicBaseUrl,
    fileMappings,
  );

  assert.deepEqual(routerCalls, [{
    path: "files/file-42",
    options: { params: {} },
  }]);
  assert.equal(response.statusCode, 200);
  assert.deepEqual(JSON.parse(response.body), {
    id: "file-42",
    url: "https://127.0.0.1:38080/files/report.pdf",
  });
});

test("drains upload request streams without concatenating buffered chunks", async () => {
  const originalConcat = Buffer.concat;

  Buffer.concat = () => {
    throw new Error("Buffer.concat should not be used while draining uploads");
  };

  try {
    await __test__.drainRequestBody(Readable.from([
      Buffer.from("chunk-1"),
      Buffer.from("chunk-2"),
    ]));
  } finally {
    Buffer.concat = originalConcat;
  }
});
