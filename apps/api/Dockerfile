FROM node:18-alpine

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Copy dependency files
COPY package.json pnpm-workspace.yaml ./
COPY apps/api/package.json ./apps/api/
COPY packages/shared/package.json ./packages/shared/

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy full source code
COPY . .

# Generate Prisma client
RUN pnpm --filter @singularity/api exec prisma generate

# Build API
RUN pnpm --filter @singularity/api run build

EXPOSE 4000

CMD ["pnpm", "--filter", "@singularity/api", "start"]
