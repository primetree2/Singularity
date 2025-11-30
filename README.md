# Singularity 🌌

A comprehensive astronomy platform for tracking celestial events, discovering dark-sky locations, and connecting with fellow stargazers.

---

## 🚀 Features

Singularity provides a complete toolkit for space enthusiasts:

1. **Tracks major astronomical events**  
2. **Real-time updates on cosmic events, ISS tracking, satellite passes, and moon phases**  
3. **Smart notifications for upcoming events near the user's location**  
4. **Advanced visibility scoring based on weather, pollution, elevation, and light pollution**  
5. **Recommends nearest dark-sky locations with high visibility scores**  
6. **Provides navigation routes to dark-site locations**  
7. **Gamified stargazing with badges, points, and visit verification**  
8. **Global leaderboard for astronomy enthusiasts**

---

## 🖼️ Screenshots (Coming Soon)

> Placeholder for UI previews once frontend pages are built  
> `(/docs/screenshots/*.png)`

---

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/primetree2/Singularity.git
cd Singularity
```

### 2. Install Dependencies

```bash
pnpm install
```

### 3. Setup Environment

```bash
cp .env.example .env
```

Update `.env` with your local credentials.

### 4. Setup Database

```bash
pnpm --filter @singularity/api exec prisma generate
pnpm --filter @singularity/api exec prisma migrate dev
pnpm --filter @singularity/api exec ts-node scripts/seed-db.ts
```

### 5. Run the App Locally

```bash
pnpm dev
```

---

## 🔐 Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | Secret key for authentication |
| `API_PORT` | Backend port (default 4000) |
| `WEB_PORT` | Frontend port (default 3000) |
| `REDIS_URL` | Redis connection string |
| `NODE_ENV` | `development` or `production` |

See: `.env.example`

---

## 📜 Scripts Reference

### Root-level Scripts

| Script | Description |
|--------|-------------|
| `pnpm bootstrap` | Install all dependencies |
| `pnpm dev` | Run all services in dev mode |
| `pnpm build` | Build all packages |
| `pnpm test` | Run all tests |
| `pnpm lint` | Lint all packages |
| `pnpm format` | Format all source files |

### Backend Scripts (@singularity/api)

| Script | Description |
|--------|-------------|
| `dev` | Run API with hot reload |
| `build` | Build production output |
| `start` | Start compiled server |
| `prisma:migrate` | Apply Prisma migrations |
| `prisma:generate` | Generate Prisma client |
| `test` | Run backend tests |

---

## 🏛️ Architecture Overview

Read the full documentation here:

- [Architecture](./docs/architecture.md)
- [API Contract](./docs/api-contract.md)
- [Visibility Algorithm](./docs/visibility-algorithm.md)
- [Onboarding Guide](./docs/onboarding.md)

---

## 🤝 Contributing

We welcome contributions!  
Read the guide here: [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 📄 License

This project is licensed under the MIT License.  
See: [LICENSE](./LICENSE)

---

## 👥 Credits

- **Harsh** – Backend, architecture, API, infrastructure
- **Rishabh** – Frontend, UI/UX, integrations

---

## 🙏 Acknowledgments

This project would not be possible without:

- NASA APIs (planned integration)
- OpenWeatherMap (future weather data)
- Mapbox (maps & route navigation)
- Prisma ORM
- Next.js frontend framework
- Express.js backend
- BullMQ, Redis, Docker, Kubernetes
- Open-source community ❤️

---

## 📧 Contact

For questions or support, please open an issue on [GitHub](https://github.com/primetree2/Singularity/issues).