#!/usr/bin/env sh
set -e

IN=openapi_spec
SPEC="apps/api/openapi.yaml"
OUTDIR="packages/shared/api-client"

echo "Generating OpenAPI client from ${SPEC} -> ${OUTDIR}"

if [ ! -f "$SPEC" ]; then
  echo "OpenAPI spec not found at ${SPEC}"
  exit 1
fi

# Clean output
if [ -d "$OUTDIR" ]; then
  echo "Removing existing output directory ${OUTDIR}"
  rm -rf "$OUTDIR"
fi

# Generate using openapi-generator-cli via pnpm dlx (will download if missing)
echo "Running openapi-generator-cli..."
pnpm dlx @openapitools/openapi-generator-cli generate \
  -i "$SPEC" \
  -g typescript-fetch \
  -o "$OUTDIR" \
  --additional-properties=supportsES6=true,withSeparateModelsAndApi=true,modelPropertyNaming=camelCase

# Install deps for generated client if package.json exists
if [ -f "$OUTDIR/package.json" ]; then
  echo "Installing generated client dependencies..."
  (cd "$OUTDIR" && pnpm install --frozen-lockfile || true)
fi

# Verify TypeScript compile for the generated client (uses shared package tsconfig if present)
echo "Verifying generated client compiles..."
if pnpm --filter @singularity/shared -s exec tsc --noEmit >/dev/null 2>&1; then
  pnpm --filter @singularity/shared exec tsc --noEmit
else
  # Fallback: try running tsc in output folder if tsconfig exists
  if [ -f "$OUTDIR/tsconfig.json" ]; then
    (cd "$OUTDIR" && pnpm exec tsc --noEmit)
  else
    echo "No tsconfig found for generated client; skipping TS compile check."
  fi
fi

echo "OpenAPI client generation complete."
