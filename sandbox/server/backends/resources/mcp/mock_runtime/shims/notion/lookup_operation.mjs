function normalizePathname(pathname) {
  if (!pathname) {
    return "/";
  }

  if (pathname.length > 1 && pathname.endsWith("/")) {
    return pathname.slice(0, -1);
  }

  return pathname;
}

function splitPathSegments(pathname) {
  return normalizePathname(pathname)
    .split("/")
    .filter(Boolean);
}

function isPlaceholderSegment(segment) {
  return segment.startsWith("{") && segment.endsWith("}");
}

function getPlaceholderName(segment) {
  return segment.slice(1, -1);
}

function matchPath(templatePath, requestPath) {
  const templateSegments = splitPathSegments(templatePath);
  const requestSegments = splitPathSegments(requestPath);

  if (templateSegments.length !== requestSegments.length) {
    return null;
  }

  const pathParams = {};
  let literalCount = 0;

  for (let index = 0; index < templateSegments.length; index += 1) {
    const templateSegment = templateSegments[index];
    const requestSegment = requestSegments[index];

    if (isPlaceholderSegment(templateSegment)) {
      pathParams[getPlaceholderName(templateSegment)] = decodeURIComponent(
        requestSegment,
      );
      continue;
    }

    if (templateSegment !== requestSegment) {
      return null;
    }

    literalCount += 1;
  }

  return {
    literalCount,
    pathParams,
  };
}

export function lookupOperation(spec, method, pathname) {
  const paths = spec?.paths;
  if (!paths || !method) {
    return null;
  }

  const normalizedPath = normalizePathname(pathname);
  const normalizedMethod = method.toLowerCase();
  const exactPathItem = paths[normalizedPath];
  const exactOperation = exactPathItem?.[normalizedMethod];

  if (exactOperation) {
    return {
      operation: exactOperation,
      pathParams: {},
    };
  }

  let bestMatch = null;

  for (const [templatePath, pathItem] of Object.entries(paths)) {
    const operation = pathItem?.[normalizedMethod];
    if (!operation) {
      continue;
    }

    const matchedPath = matchPath(templatePath, normalizedPath);
    if (!matchedPath) {
      continue;
    }

    const candidate = {
      operation,
      pathParams: matchedPath.pathParams,
      score: matchedPath.literalCount,
      templatePath,
    };

    if (
      !bestMatch
      || candidate.score > bestMatch.score
      || (
        candidate.score === bestMatch.score
        && candidate.templatePath < bestMatch.templatePath
      )
    ) {
      bestMatch = candidate;
    }
  }

  if (!bestMatch) {
    return null;
  }

  return {
    operation: bestMatch.operation,
    pathParams: bestMatch.pathParams,
  };
}
