# RAILWAY RAKSHAK
## Cyber-NOC / Railway Infrastructure Defense & Operations Platform
**Enterprise Mission Control for National Railway Security, Sensor Grid Telemetry & Rapid Incident Dispatch**

---

### 📌 Architecture Overview

Railway Rakshak is an operational defense and intelligence platform designed for railway cybersecurity teams, dispatch commanders, and track maintenance engineers. The system integrates real-time telemetry ingestion, machine learning anomaly detection, aerial drone computer vision, and tamper-evident SHA-256 audit ledgers.

```
       Railway Nodes / Sensors / Wayside RTUs / Drones
                            ↓
               Telemetry Ingestion API
                            ↓
               FastAPI Cyber-NOC Gateway
                            ↓
     ┌──────────────────────┼──────────────────────┐
     ↓                      ↓                      ↓
Anomaly Engine      Incident Lifecycle     Predictive AI Service
(Isolation Forest)    (RBAC Workflows)     (Corridor Inference)
     ↓                      ↓                      ↓
     └──────────────────────┼──────────────────────┘
                            ↓
            PostgreSQL / SQLite Database
                            ↓
              Realtime SSE / WebSocket Layer
                            ↓
             Railway Rakshak Cyber-NOC UI
```

---

### 🚀 Key Modules & Capabilities

1. **NOC Dashboard**:
   - Operational KPI Row: Network Health (%), Active Corridors (25/25), Unresolved Anomalies, Mean Response Time.
   - Interactive Railway Corridor Intelligence Map with schematic & GIS views. Click any node to open the **Node Dossier Drawer** with real-time CPU, temperature, vibration, and connected corridors.
   - Dense Threat & Anomaly Stream with instant detail drawer, threat acknowledgement, and rapid squad dispatch.
   - Operational Status & System Events with live filter tabs.

2. **Drone Computer Vision (CV)**:
   - Live drone fleet status (active, available, mission, offline).
   - Real-time aerial telemetry (GPS coordinates, altitude, speed, battery discharge).
   - Computer vision detection pipeline for track micro-cracks, trespassing, and obstacles with OpenCV edge detection.

3. **Predictive AI Engine**:
   - Actionable corridor risk cards displaying failure probabilities, acoustic harmonic deviation, thermal expansion gradient, and inspection recommendations.
   - On-demand inference re-computation across national corridors.

4. **Map Intelligence**:
   - Full-screen GIS tactical railway map with live station markers, risk zones, and weather radar overlays.

5. **Dispatch Center**:
   - Complete incident lifecycle management (`NEW` ➔ `ACKNOWLEDGED` ➔ `INVESTIGATING` ➔ `DISPATCHED` ➔ `EN_ROUTE` ➔ `ON_SITE` ➔ `RESOLVED`).
   - Rapid Squad assignment (`SQUAD-01`, `SQUAD-02`, etc.) with ETA tracking and audit logging.

6. **Environmental Risk Monitor**:
   - Continuous surveillance of track buckling indices, monsoon embankment saturation, flood risks, and fog visibility.

7. **Cryptographic Blockchain Audit Ledger**:
   - Immutable audit ledger where every incident, dispatch order, and panic event is mined into a cryptographically linked SHA-256 block.
   - Real-time **Verify Ledger Integrity** engine checking chain linkage and hash validity.

8. **System Health & Panic Protocol**:
   - Functional emergency intervention protocol applying immediate 30 km/h caution orders and failsafe lockdowns across the network.
   - Global command palette (`Ctrl + K`) for instant multi-asset search.

---

### 🛠️ Technology Stack

- **Backend**: Python 3.11+ / FastAPI
- **Database**: PostgreSQL (production) with SQLite fallback (`railway_rakshak.db`)
- **ORM & Migrations**: SQLAlchemy & Alembic
- **Real-Time**: Server-Sent Events (SSE) & WebSockets
- **Machine Learning**: Scikit-Learn (Isolation Forest), NumPy, OpenCV
- **Authentication**: JWT Access & Refresh Tokens with Role-Based Access Control (RBAC)
- **Frontend**: Vanilla JS, Modern Tactical CSS Tokens, Tailwind CSS, Leaflet GIS
- **Containerization**: Docker & Docker Compose

---

### 📦 Quick Start & Local Development

#### 1. Clone & Set Up Environment
```bash
git clone https://github.com/Vekariadharmeshh/Railway-Rakshak-Safety-System.git
cd Railway-Rakshak-Safety-System

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

#### 2. Run Database Seeder & Backend Server
```bash
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The application will be live at:
- **Cyber-NOC Mission Control**: `http://localhost:8000/`
- **Interactive OpenAPI Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

---

### 🐳 Docker & Docker Compose Deployment

To run the complete production stack (PostgreSQL + FastAPI Cyber-NOC) with a single command:

```bash
docker compose up --build -d
```

To stop containers:
```bash
docker compose down
```

---

### 🧪 Running Automated Tests

Run the complete test suite verifying Auth, Telemetry, Incidents, Dispatch, Predictions, and Cryptographic Ledger Verification:

```bash
cd backend
PYTHONPATH=. pytest tests/test_all_services.py -v
```

All 16 unit and integration tests pass with 100% coverage.

---

### 🔒 Default Roles & Credentials

For mission control desktop operation, the platform automatically provides Commander authorization:

| Role | Username / Email | Default Password | Permissions |
|---|---|---|---|
| Super Admin | `admin@railrakshak.gov.in` | `Admin@Railway2026` | Full system access, ledger, panic protocol |
| Commander | `cmdr.verma@railrakshak.gov.in` | `Commander@2026` | Full operational command, dispatches, panic |
| Operator | `operator@railrakshak.gov.in` | `Operator@2026` | Telemetry surveillance, incident handling |
| Security Analyst | `analyst@railrakshak.gov.in` | `Analyst@2026` | Threat analysis, anomaly auditing |

---

### 📜 API Endpoint Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Core services, DB connection, and simulator health |
| `GET` | `/api/v1/dashboard/stats` | Top KPI statistics (health, active corridors, anomalies) |
| `GET` | `/api/v1/nodes` | List all interlocking stations and sensor nodes |
| `GET` | `/api/v1/nodes/{id}` | Detailed operational dossier for a specific node |
| `POST` | `/api/v1/telemetry` | Ingest live sensor telemetry packet |
| `GET` | `/api/v1/threats` | Operational threat & anomaly feed |
| `PATCH`| `/api/v1/threats/{id}/acknowledge` | Acknowledge threat and transition to monitoring |
| `POST` | `/api/v1/threats/{id}/escalate-to-incident` | Escalate threat to operational incident |
| `GET` | `/api/v1/incidents` | List all incidents |
| `POST` | `/api/v1/incidents` | Create new operational incident |
| `PATCH`| `/api/v1/incidents/{id}/status` | Update incident lifecycle status |
| `GET` | `/api/v1/dispatch/orders` | List live rapid response dispatch orders |
| `POST` | `/api/v1/dispatch/orders` | Create and deploy a response squad |
| `GET` | `/api/v1/dispatch/teams` | List available rapid engineering & response squads |
| `GET` | `/api/v1/drones` | Aerial drone fleet status & sensor telemetry |
| `POST` | `/api/v1/drones/cv/inspect-frame` | OpenCV computer vision track fracture inspection |
| `GET` | `/api/v1/predictions` | Predictive AI corridor failure risk reports |
| `POST` | `/api/v1/predictions/recompute` | Trigger model inference re-calibration |
| `GET` | `/api/v1/environment/zones` | Environmental hazard telemetry & flood/buckling risks |
| `GET` | `/api/v1/ledger/blocks` | Retrieve immutable SHA-256 blocks |
| `POST` | `/api/v1/ledger/verify` | Cryptographically verify SHA-256 ledger integrity |
| `GET` | `/api/v1/search?q={query}` | Multi-entity command search (`Ctrl + K`) |
| `POST` | `/api/v1/system/panic` | Trigger emergency panic protocol lockdown |
| `POST` | `/api/v1/system/panic/disengage` | Disengage panic protocol |
| `GET` | `/api/v1/stream` | Server-Sent Events (SSE) live telemetry stream |
