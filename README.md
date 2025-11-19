# 🚀 Singularity

Singularity is a modern web application built for space enthusiasts. It helps users track astronomical events, analyze visibility conditions, discover dark sites, receive notifications, and gamify the stargazing experience with badges and leaderboards.

## 🌌 Features
- Track major astronomical events in real-time  
- Visibility scoring based on weather, pollution, light pollution, elevation, moon phase, and more  
- Find the nearest dark-sky locations for perfect stargazing  
- Push notifications for upcoming or nearby cosmic events  
- Gamification system with badges, points, and an international leaderboard  

## 🛠️ Tech Stack
- **Frontend:** Next.js (TypeScript)  
- **Backend:** Express (TypeScript)  
- **Database:** Prisma ORM  
- **Monorepo:** pnpm workspaces  
- **Other:** Docker, OpenAPI, BullMQ (workers), Redis, Postgres  

---

## 📦 Getting Started

Install dependencies:

```sh
pnpm install
Start all apps in dev mode:

pnpm dev

📁 Project Structure
singularity/
├── apps/
│   ├── web/        # Next.js frontend (Rishabh)
│   └── api/        # Express backend (Harsh)
└── packages/
    └── shared/     # Shared types, utilities, and API client

🤝 Contributing

This project is developed by:

Harsh — Backend, infrastructure, core architecture

Rishabh — Frontend, UI/UX, client integration

Pull requests and improvements are welcome as the project evolves.

📜 License

See the LICENSE file for details.