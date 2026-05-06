const MOCK_CANVAS_PREFIX = "https://mock-canvas.local/";

export function rewriteCanvasPublicUrl(url, publicBaseUrl) {
  if (typeof url !== "string" || !url.startsWith(MOCK_CANVAS_PREFIX)) {
    return url;
  }

  const sourceUrl = new URL(url);
  const targetUrl = new URL(publicBaseUrl);

  targetUrl.pathname = sourceUrl.pathname;
  targetUrl.search = sourceUrl.search;
  targetUrl.hash = sourceUrl.hash;

  return targetUrl.toString();
}
