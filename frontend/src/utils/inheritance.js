function cloneJson(x) {
  try {
    return structuredClone(x)
  } catch {
    return JSON.parse(JSON.stringify(x))
  }
}

/**
 * Deep-merge document overlay (same rules as backend): objects merge recursively;
 * arrays and scalars from overlay replace at that key.
 */
export function deepMergeDocument(base, overlay) {
  if (
    base !== null &&
    typeof base === 'object' &&
    !Array.isArray(base) &&
    overlay !== null &&
    typeof overlay === 'object' &&
    !Array.isArray(overlay)
  ) {
    const out = { ...base }
    for (const key of Object.keys(overlay)) {
      const v = overlay[key]
      if (
        key in out &&
        out[key] !== null &&
        typeof out[key] === 'object' &&
        !Array.isArray(out[key]) &&
        v !== null &&
        typeof v === 'object' &&
        !Array.isArray(v)
      ) {
        out[key] = deepMergeDocument(out[key], v)
      } else {
        out[key] = v !== undefined ? cloneJson(v) : v
      }
    }
    return out
  }
  return cloneJson(overlay)
}

/**
 * Compose resolved schema fragment for preview: parent is already fully resolved.
 */
export function composeSchemaResolved(parentResolved, localFragment) {
  return { allOf: [cloneJson(parentResolved), cloneJson(localFragment)] }
}
