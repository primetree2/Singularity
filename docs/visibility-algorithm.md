# Singularity Visibility Algorithm Documentation

## 1. Overview

The **visibility score** is a computed metric (0–100) that represents how clearly a user can observe an astronomical event from a given location at a given time.  
It balances environmental, atmospheric, and astronomical conditions to estimate observation clarity.

This document describes the algorithm currently implemented in the system, including factors, weights, and future upgrade plans.

---

## 2. Visibility Factors

The algorithm currently evaluates **six primary factors**, each normalized to a 0–1 or 0–500 range depending on data source.

### **Factors & Meaning**
| Factor | Description | Ideal Value |
|--------|-------------|-------------|
| **cloudCover** | % of sky obstructed by clouds | 0 (clear sky) |
| **aqi** | Air Quality Index | 0 (clean air) |
| **lightPollution** | Brightness due to artificial light | 0 (dark sky) |
| **elevation** | Height above sea level (meters) | High |
| **moonIllumination** | Fraction of moon illuminated | 0 (new moon) |
| **horizon** | Extent of visible horizon | High |

---

## 3. Weights

Each factor is weighted to reflect its impact on astronomical visibility.

| Factor | Weight |
|--------|--------|
| cloudCover | **0.25** |
| aqi | **0.15** |
| lightPollution | **0.20** |
| elevation | **0.10** |
| moonIllumination | **0.15** |
| horizon | **0.15** |

Weights sum to **1.00**.

---

## 4. Normalization Rules

To maintain comparability:

### **cloudCover (0–1)**  
Lower is better → normalized value = (1 - cloudCover)

### **aqi (0–500)**  
AQI is inverted and scaled:  
`aqiNorm = max(0, 1 - (aqi / 500))`

### **lightPollution (0–1)**  
Lower is better → normalized value = (1 - lightPollution)

### **elevation (0–3000 m)**  
Higher is better → `elevationNorm = elevation / 3000` (clamped 0–1)

### **moonIllumination (0–1)**  
Lower is better → `moonNorm = (1 - moonIllumination)`

### **horizon (0–1)**  
Higher is better → horizonNorm = horizon

---

## 5. Final Score Formula

score =
cloudCoverNorm * 0.25 +
aqiNorm * 0.15 +
lightPollutionNorm * 0.20 +
elevationNorm * 0.10 +
moonNorm * 0.15 +
horizonNorm * 0.15

css
Copy code

Then scaled to a **0–100** score:

visibilityScore = round(score * 100)

yaml
Copy code

---

## 6. Example Calculation

### Example Inputs:
cloudCover: 0.20
aqi: 75
lightPollution: 0.30
elevation: 500
moonIllumination: 0.60
horizon: 0.80

shell
Copy code

### Normalized:
cloudCoverNorm = 0.80
aqiNorm = 1 - (75/500) = 0.85
lightPollutionNorm = 0.70
elevationNorm = 500/3000 ≈ 0.167
moonNorm = 0.40
horizonNorm = 0.80

shell
Copy code

### Apply Weights:
score =
0.80 * 0.25 = 0.20
0.85 * 0.15 = 0.1275
0.70 * 0.20 = 0.14
0.167 * 0.10 = 0.0167
0.40 * 0.15 = 0.06
0.80 * 0.15 = 0.12

shell
Copy code

### Final:
Total = 0.6642
visibilityScore = 66

yaml
Copy code

---

## 7. Future Improvements

Planned enhancements:

### **1. Real-time weather integration**
- Cloud cover from **OpenWeather / NOAA**
- Humidity and temperature

### **2. Air quality data**
- AQI from **IQAir**, **OpenAQ**, or local sensors

### **3. Light pollution mapping**
- SQM data from satellite surveys  
- Integration with "DarkSiteFinder" datasets

### **4. Moon position + altitude**
- Not just illumination  
- Horizon angle effects

### **5. Atmospheric extinction modeling**
- Based on Rayleigh scattering  
- Helps deep-sky observation accuracy

### **6. Machine learning scoring refinement**
- Train ML model on user-submitted “visibility ratings”

---

## 8. External Data Sources (Planned)

| Data Type | Provider | Notes |
|-----------|----------|-------|
| Weather | OpenWeatherMap, NOAA | Cloud %, humidity, pressure |
| AQI | IQAir API, OpenAQ | Real-time AQI |
| Light Pollution | World Atlas of Artificial Night Sky Brightness | Satellite data |
| Moon Phases | US Naval Observatory, NASA | Moon illumination & position |
| Satellite Passes | Celestrak, Heavens-Above | TLE data for ISS + satellites |

---

**The visibility algorithm will iteratively improve as more real-world data is integrated into