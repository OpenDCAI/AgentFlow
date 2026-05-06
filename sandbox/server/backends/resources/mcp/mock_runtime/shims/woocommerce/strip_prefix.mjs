const WOO_PREFIX = "/wp-json/wc/v3/";

export function stripWooPrefix(pathname) {
  if (!pathname.startsWith(WOO_PREFIX)) {
    throw new Error(`WooCommerce REST prefix not found: ${pathname}`);
  }

  return pathname.slice(WOO_PREFIX.length);
}
