#!/usr/bin/env sh
set -e

echo "==> Singularity dev setup"

# Check Node version >= 18
if ! command -v node >/dev/null 2>&1; then
  echo "Node is not installed. Please install Node 18+."
  exit 1
fi

NODE_VERSION="$(node -v | sed 's/v//')"
MAJOR="$(printf "%s" "$NODE_VERSION" | cut -d. -f1)"

if [ -z "$MAJOR" ] || [ "$MAJOR" -lt 18 ]; then
  echo "Node version $NODE_VERSION detected. Node 18+ is required."
  exit 1
fi

echo "Node $NODE_VERSION detected."

# Check pnpm
if ! command -v pnpm >/dev/null 2>&1; then
  echo "pnpm is not installed. Install it: npm i -g pnpm"
  exit 1
fi

echo "pnpm detected: $(pnpm -v)"

echo "Installing dependencies..."
pnpm install --frozen-lockfile

# Copy .env.example to .env if not exists
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
  else
    echo "No .env.example found. Please create .env manually."
  fi
else
  echo ".env already exists"
fi

# Generate Prisma client
echo "Generating Prisma client..."
# prefer package script if present, otherwise use prisma directly
if pnpm --filter @singularity/api -s -v >/dev/null 2>&1; then
  if pnpm --filter @singularity/api -s run prisma:generate >/dev/null 2>&1; then
    pnpm --filter @singularity/api run prisma:generate
  else
    pnpm --filter @singularity/api exec prisma generate --schema=src/db/prisma/schema.prisma || true
  fi
else
  pnpm exec prisma generate --schema=apps/api/src/db/prisma/schema.prisma || true
fi

# Run migrations
echo "Applying Prisma migrations..."
if pnpm --filter @singularity/api -s run prisma:migrate >/dev/null 2>&1; then
  pnpm --filter @singularity/api run prisma:migrate
else
  pnpm --filter @singularity/api exec prisma migrate dev --schema=src/db/prisma/schema.prisma || true
fi

# Run seed script
echo "Seeding database..."
if [ -f apps/api/src/db/seeds/seed.ts ]; then
  if pnpm --filter @singularity/api -s exec tsx --version >/dev/null 2>&1; then
    pnpm --filter @singularity/api exec tsx apps/api/src/db/seeds/seed.ts || true
  elif pnpm --filter @singularity/api -s exec ts-node --version >/dev/null 2>&1; then
    pnpm --filter @singularity/api exec ts-node apps/api/src/db/seeds/seed.ts || true
  else
    echo "tsx/ts-node not available in @singularity/api. Attempting prisma db seed..."
    pnpm --filter @singularity/api exec prisma db seed --schema=src/db/prisma/schema.prisma || true
  fi
else
  echo "No seed script found at apps/api/src/db/seeds/seed.ts"
fi

echo ""
echo "Setup complete ✅"
echo ""
echo "Next steps:"
echo "  - Start development: pnpm dev"
echo "  - API: pnpm --filter @singularity/api dev"
echo "  - Web: pnpm --filter @singularity/web dev"
echo ""
echo "Happy stargazing! 🌌"
