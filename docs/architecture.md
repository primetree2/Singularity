# Singularity – System Architecture Documentation

## 1. Overview

**Singularity** is a modular, scalable, cloud-ready platform designed for astronomy enthusiasts.  
It tracks astronomical events, computes visibility conditions, recommends dark sites, and provides a gamified user experience.  
The system is built using a **TypeScript pnpm monorepo** containing:

- **Frontend (Next.js)** – The user-facing web interface  
- **Backend API (Express.js + Prisma)** – Core logic, event tracking, visibility scoring, gamification  
- **Shared Package** – Shared types, DTOs, utilities  
- **Infrastructure (Terraform + Kubernetes)** – Deployment architecture  
- **Workers** – Notification and event-fetch background processors  

---

## 2. Technology Stack

### **Backend**
- Node.js 18+
- Express.js  
- Prisma ORM (PostgreSQL)
- Redis (caching + worker queues)  
- BullMQ (Workers)  
- JWT Authentication  
- OpenAPI 3.0 for API contract

### **Frontend**
- Next.js (React + TypeScript)
- TailwindCSS
- Mapbox API
- Client generated from OpenAPI spec

### **Infrastructure**
- Docker & Docker Compose
- Kubernetes (Ingress, Deployments, Services)
- Terraform provisioning (VPC, RDS, Redis, ECS/EKS)
- NGINX reverse proxy

---

## 3. Database Schema Diagram (Text/ASCII)

+--------------------+ +-------------------+
| User | | Event |
+--------------------+ +-------------------+
| id (PK) | | id (PK) |
| email (unique) | | title |
| password | | description |
| displayName | | start |
| score | | end |
| createdAt | | type |
| updatedAt | | lat, lon |
+---------+----------+ +----------+--------+
| ^
| |
v |
+--------------------+ +--------+-----------+
| UserBadge | | Visit |
+--------------------+ +--------------------+
| id (PK) | | id (PK) |
| userId (FK) |------->| userId (FK) |
| badgeId (FK) | | eventId (FK) |
| earnedAt | | darkSiteId (FK) |
+--------------------+ | timestamp |
| photoUrl |
+--------------------+ | visibilityScore |
| Badge | | points |
+--------------------+ +--------------------+
| id (PK) |
| name (unique) |
| description | +--------------------+
| iconUrl | | DarkSite |
| pointsRequired | +--------------------+
+--------------------+ | id (PK) |
| name |
| lat, lon |
| lightPollution |
| description |
+--------------------+

+--------------------+
| DeviceToken |
+--------------------+
| id (PK) |
| userId (FK) |
| token |
| platform |
| createdAt |
+--------------------+

markdown
Copy code

---

## 4. API Architecture

### **Structure**
- REST API with OpenAPI 3.0 contract  
- Modular route structure:
  - `/users`
  - `/events`
  - `/darksites`
  - `/visits`
  - `/leaderboard`
  - `/notifications`
  - `/health`

### **Key Services**
- **Events Service** – Fetch events, event metadata, dynamic updates  
- **Visibility Service** – Compute visibility score using environmental factors  
- **Dark Site Service** – Geographic calculations and ranking  
- **Gamification Service** – Points, badges, visits  
- **Notifications Service** – Device token management, push system  
- **Workers** – Daily event fetcher, notification dispatcher

---

## 5. Frontend Architecture

### **Structure**
apps/web/
├── pages/
├── components/
├── hooks/
├── services/
├── styles/
├── utils/
└── lib/

markdown
Copy code

### **Page Flow**
- `/` – Home (event list)
- `/events/:id`
- `/dashboard`
- `/darksites`
- `/auth/login`
- `/auth/register`

### **State Management**
- React + SWR or React Query  
- User session stored via JWT in cookies or secure storage  
- Visibility and dark-site data fetched from backend

### **Maps**
- Mapbox for dark site recommendations and event overlays

---

## 6. Data Flow Diagrams

### **User Registration Login Flow**
[Frontend] → POST /users/register → [API] → [DB]
[Frontend] ←------ JWT token ------← [API]

[Frontend] → POST /users/login → [API]
←------ JWT token ------←

markdown
Copy code

### **Visibility Score Calculation**
User Location → API → Visibility Service
→ Factor Computation
→ Weighted Score
← VisibilityScore

markdown
Copy code

### **Dark Site Recommendation**
User (lat, lon)
→ API
→ Fetch all dark sites
→ Sort by Haversine distance
← Return nearest sites

markdown
Copy code

### **Visit & Gamification Flow**
User Visit Report → API
→ computeVisibility()
→ createVisit()
→ awardPoints()
→ checkAndAwardBadges()
← Return visit + badges

markdown
Copy code

### **Notifications Flow**
User Device Token → /notifications/device-token
Background Job → sendPushNotification()

markdown
Copy code

---

## 7. Security Considerations

- **JWT Authentication** for all protected routes  
- **Password hashing (bcrypt)**  
- **HTTPS mandatory** in production  
- **CORS configuration** for browser clients  
- **Input validation** for all API endpoints  
- **Rate limiting** recommended (NGINX / API Gateway)  
- **Secrets management** via:
  - AWS Secrets Manager  
  - Kubernetes Secrets  
  - `.env` files only for local use  

---

## 8. Scalability Notes

- Stateless API → horizontally scalable via containers  
- PostgreSQL RDS can scale vertically or via read replicas  
- Redis used for:
  - Caching heavy computations (visibility)  
  - Worker queues for notifications & event fetching  
- CDN recommended for static assets  
- Load balancing handled via:
  - NGINX reverse proxy (local)  
  - Kubernetes Ingress (production)  

### Future Scalability Upgrades
- Event-driven microservices  
- Distributed caching  
- Sharded data stores for extremely large event datasets  
- Streaming astronomy data ingestion

---

**End of Architecture Document**