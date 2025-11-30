# Developer Onboarding Guide — Singularity

Welcome to **Singularity**, a modular TypeScript monorepo powering astronomical event tracking, visibility scoring, dark-site discovery, and gamified stargazing.

This guide ensures you can set up, develop, and contribute smoothly.

---

## 1. Prerequisites

Make sure you have the following installed:

### Required Tools

- **Node.js ≥ 18**
- **pnpm ≥ 8**  
  Install: `npm install -g pnpm`
- **PostgreSQL ≥ 15**
- **Redis ≥ 7**
- **Git**

### Optional

- Docker & Docker Compose (for containerized development)

---

## 2. Setup Steps

The repo includes an automated setup script:

### **Run the full setup**

```bash
./scripts/setup-dev.sh
```

This script will:

- Validate Node & pnpm versions
- Install dependencies
- Copy `.env.example` → `.env` if missing
- Generate Prisma client
- Apply DB migrations
- Seed initial data
- Print next steps

You may need to give execution permission:

```bash
chmod +x scripts/*.sh
```

---

## 3. Environment Configuration

Configuration lives in the root `.env` file.

### Important variables:

```ini
DATABASE_URL=postgresql://user:password@localhost:5432/singularity
REDIS_URL=redis://localhost:6379
API_PORT=4000
WEB_PORT=3000
```

Update values according to your local PostgreSQL/Redis setup.

---

## 4. Running the Project Locally

### Start all services

```bash
./scripts/start-all.sh
```

This:

- Starts API (`apps/api`) on port 4000
- Starts Web (`apps/web`) on port 3000

### Start each manually

**API**

```bash
cd apps/api
pnpm dev
```

**Web**

```bash
cd apps/web
pnpm dev
```

---

## 5. Running Tests

### All tests:

```bash
pnpm test
```

### Specific package:

```bash
pnpm --filter <package> test
```

### Example:

```bash
pnpm --filter @singularity/api test
```

---

## 6. Making Changes

### General Rules

All code must pass:

- ESLint
- Prettier
- TypeScript type checks
- Unit tests

Additional requirements:

- API must remain consistent with the OpenAPI spec
- Breaking changes require discussion + PR tag

### Adding or modifying API endpoints

1. Update `apps/api/openapi.yaml`
2. Regenerate API client:
   ```bash
   ./scripts/gen-openapi-client.sh
   ```
3. Update implementation in `apps/api`
4. Update frontend usage if needed

---

## 7. Submitting Pull Requests

### Branch Naming

```
feature/<your-feature>
bugfix/<your-fix>
chore/<task>
docs/<documentation>
```

### PR Requirements

- Description of the change
- Link to issue (if applicable)
- Screenshots (frontend)
- Tests for new functionality
- Updated OpenAPI spec (backend endpoints)
- Follow code style guides

### CI Must Pass

- Lint
- Typecheck
- Tests
- OpenAPI validation
- Build

---

## 8. Code Style Guide

### Formatting

Prettier handles formatting

Run manually:

```bash
pnpm format
```

### Linting

```bash
pnpm lint
```

### TypeScript Rules

- Strict mode on
- Avoid `any`
- Prefer explicit types for public functions
- Use shared types from `@singularity/shared`

### Folder Conventions

- Keep business logic in services
- Database access in models
- No external API calls in controllers
- Use utils for pure functions

---

## 9. Troubleshooting

### ❌ pnpm install fails inside shared package

- Ensure `package.json` exists in every workspace directory
- Remove stray empty files

### ❌ Prisma migration errors

```bash
pnpm --filter @singularity/api exec prisma migrate reset
```

### ❌ Ports already in use

API uses `4000`, Web uses `3000`

Find and kill process:

```bash
lsof -i :4000
kill -9 <PID>
```

### ❌ Redis/PostgreSQL connection failures

- Ensure services are running
- Verify credentials in `.env`

### ❌ Types not recognized

Run:

```bash
pnpm --filter @singularity/shared build
```

---

## 10. You're Ready!

With local setup, testing, and workflows in place, you can now build features confidently and contribute effectively.

**Happy building — and clear skies!** 🌌