# 🚀 Singularity — Astro-Service API Reference

> Backend service for astronomical predictions, visibility scoring, and event data.
>
> Base URL (local): `http://localhost:8000`  
> Base URL (production example): `https://astro.singularity.app`

---

## 🛰️ Overview

The **Astro-Service** provides REST endpoints for:

| Category | Description |
|-----------|--------------|
| `/predictions/*` | Predict satellite passes & visibility scores |
| `/satellites/*` | Access TLE and satellite metadata |
| `/health`, `/ready` | Service health & readiness checks |

The service is built on **FastAPI** with async endpoints and integrates:
- Skyfield + SGP4 for orbital mechanics  
- Custom visibility scoring (clouds + light pollution + geometry)  
- Cached TLE retrieval from [Celestrak](https://celestrak.org)  

---

## 🔧 Authentication

> Currently **no authentication required** (development phase).  
Future versions may require an API key via header:  
`Authorization: Bearer <token>`.

---

## 🌐 **Endpoints**

### 1️⃣ `GET /`
**Purpose:** Basic status check.

**Response 200:**
```json
{
  "service": "singularity-astro-service",
  "version": "0.1.0",
  "status": "ok"
}
2️⃣ GET /health
Purpose: Health summary of all components.

Response 200:

json
Copy code
{
  "status": "ok",
  "service": "singularity-astro-service",
  "version": "0.1.0",
  "predictor": "ready",
  "tle_manager": "ready"
}
Status codes:

200 OK — all components ready

503 Service Unavailable — if degraded or missing components

3️⃣ GET /ready
Purpose: Kubernetes-style readiness probe.
Returns ready=true if service is initialized and can process requests.

Response:

json
Copy code
{
  "ready": true,
  "details": {
    "tle_manager": "present"
  }
}
4️⃣ GET /satellites/list
Purpose: List available satellites from TLE source.

Query Params:

Name	Type	Default	Description
source	string	"celestrak_stations"	Which TLE group to fetch (stations, starlink, active, etc.)
limit	integer	50	Optional max number of satellites to return

Example Request:

bash
Copy code
GET /satellites/list?source=celestrak_stations&limit=5
Response 200:

json
Copy code
{
  "count": 5,
  "source": "celestrak_stations",
  "satellites": [
    {"name": "ISS (ZARYA)", "line1": "1 25544U 98067A ...", "line2": "2 25544 ...", "epoch": "2025-11-12T00:00:00Z"},
    {"name": "TIANGONG", "line1": "...", "line2": "..."}
  ]
}
5️⃣ GET /predictions/satellite
Purpose: Predict visibility of a given satellite for a specific observer location/time.

Query Params:

Name	Type	Required	Example	Description
satellite_name	string	✅	ISS	Satellite common name
lat	float	✅	28.6139	Observer latitude (deg)
lng	float	✅	77.2090	Observer longitude (deg)
time	ISO 8601	optional	2025-11-12T18:00:00Z	Observation time (UTC). Defaults to now.
elevation_m	float	optional	250	Observer elevation (m)
cloud_cover	float	optional	10	Cloud cover % (0–100)
light_pollution	float	optional	0.4	Light pollution index 0–1
source	string	optional	celestrak_stations	TLE source group

Example Request:

bash
Copy code
GET /predictions/satellite?satellite_name=ISS&lat=28.6139&lng=77.2090
Response 200:

json
Copy code
{
  "satellite": "ISS",
  "observer": {
    "latitude": 28.6139,
    "longitude": 77.2090,
    "elevation_m": 250
  },
  "observation_time": "2025-11-12T18:00:00Z",
  "satellite_geometry": {
    "altitude": 52.3,
    "azimuth": 187.5,
    "is_above_horizon": true
  },
  "sun_position": {"altitude": -24.8},
  "moon_position": {"altitude": -5.2, "illumination_percent": 8.4},
  "visibility": {
    "overall_score": 78.2,
    "breakdown": {
      "elevation_factor": 0.82,
      "sun_factor": 0.95,
      "cloud_factor": 0.9,
      "light_pollution_factor": 0.8
    }
  },
  "visible": true,
  "recommended": true
}
Response 404 (satellite not found):

json
Copy code
{
  "error": "Satellite not found: ISS-XYZ",
  "visible": false
}
6️⃣ GET /predictions/next-passes
Purpose: Find upcoming visible passes for a given satellite and location.

Query Params:

Name	Type	Required	Example	Description
satellite_name	string	✅	ISS	Satellite name
lat	float	✅	37.7749	Observer latitude
lng	float	✅	-122.4194	Observer longitude
days_ahead	int	optional	7	How many days ahead to search
min_score	float	optional	50	Only include passes with score ≥ this
cloud_cover	float	optional	0	Cloud cover %
light_pollution	float	optional	0.3	Light pollution index 0–1

Example Request:

vbnet
Copy code
GET /predictions/next-passes?satellite_name=ISS&lat=37.7749&lng=-122.4194
Response 200:

json
Copy code
{
  "satellite": "ISS",
  "count": 3,
  "passes": [
    {
      "peak_time_iso": "2025-11-12T18:20:00Z",
      "start_time_iso": "2025-11-12T18:15:00Z",
      "end_time_iso": "2025-11-12T18:25:00Z",
      "max_elevation_deg": 68.3,
      "score": 86.4
    },
    {
      "peak_time_iso": "2025-11-13T19:03:00Z",
      "start_time_iso": "2025-11-13T18:59:00Z",
      "end_time_iso": "2025-11-13T19:09:00Z",
      "max_elevation_deg": 44.5,
      "score": 72.1
    }
  ]
}
🧠 Scoring Model
Visibility scoring integrates several physical factors:

Factor	Range	Meaning
Elevation (°)	0–90	Higher → better visibility
Sun altitude (°)	Below –12 = night	Sun below horizon improves score
Cloud cover (%)	0–100	Clouds reduce score
Light pollution (0–1)	Lower = darker sky	
Moon illumination (%)	Affects background brightness	
Airmass	Lower = clearer line-of-sight	

overall_score ≈ weighted sum of these factors, normalized to 0–100.

⚙️ Error Responses
Code	Meaning	Example
400	Bad input or missing parameters	{"detail": "lat/lng required"}
404	Satellite not found	{"error": "Satellite not found: X"}
500	Internal server error	{"detail": "Internal server error"}

🧩 Development Notes
Local start:

bash
Copy code
cd astro-service
uvicorn app.main:app --reload --port 8000
Test suite:

bash
Copy code
pytest astro-service/tests -q
Prefetched TLEs cached in memory for 6 hours (default).

Uses Celestrak “stations” group for ISS by default.

🔮 Future Planned Endpoints
Endpoint	Purpose	Status
/predictions/starlink	Predict visibility for Starlink trains	🕐 Planned
/predictions/meteors	Meteor-shower predictions	🕐 Planned
/dark-sites/nearby	Suggest optimal viewing locations	🕐 Planned
/notifications/push	Schedule sighting alerts	🕐 Planned

🧾 Changelog
Version	Date	Changes
0.1.0	2025-11-12	Initial MVP release — ISS predictions, health endpoints
0.2.0	TBD	Add Starlink & weather/light pollution factors

Maintainers:
Harsh Raj (@primetree2) & Rishabh Khanna
© 2025 Singularity Project — All Rights Reserved

yaml
Copy code

---

### ✅ Next Steps
- Place this file at:  
singularity/docs/API.md

javascript
Copy code
- Run your service locally (`uvicorn app.main:app --reload`) and visit  
[`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs) for auto-generated Swagger UI — this Markdown complements it for external developers or the frontend team.