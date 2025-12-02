# Harit Samarth — Climate-Smart Advisory Platform

Harit Samarth helps Indian farmers make data-backed decisions about crop planning, soil health, subsidy access, and IoT hardware usage. The platform combines a Vite/React frontend, a Flask backend with dual MySQL + CSV persistence, Supabase integrations, and an internal machine-learning pipeline for crop recommendations.

---

## 1. Features
- Climate-aware UX with hero, chatbot widget, hardware showcases, and regional insights.
- Interactive modules for crop recommendations, soil health reports, subsidy discovery, and soil hardware telemetry.
- Backend ingestion pipeline that stores every soil-health analysis in both MySQL and CSV, with automatic fallback when the database is unavailable.
- Supabase integration for authentication and future data sync.
- Regional crop recommendation dataset (`data/crop_recommendations.csv`) covering Indian agro-climatic zones.
- Random Forest classifier (`backend/train_crop_model.py`) that learns from regional climate, soil, and risk features to propose the best crop.
- WeatherAPI-powered, location-aware crop recommendations surfaced via the React UI with detailed crop advisory pages.
- Diagnostics toolkit (e.g., `backend/debug_mysql.py`) for validating infrastructure readiness.

---

## 2. Architecture Overview
| Layer    | Technology & Tools                                                                 | Notes |
|----------|-------------------------------------------------------------------------------------|-------|
| Frontend | React 18, Vite, TypeScript, Tailwind CSS, shadcn/ui                                | SPA served through Vite dev server or static host |
| Backend  | Flask, mysql-connector-python, python-dotenv, logging                               | Soil health API, ML inference hooks, diagnostics |
| Data     | MySQL (primary), CSV (redundant logging), Supabase                                  | Dual-write ensures offline durability |
| ML       | pandas, scikit-learn, joblib                                                        | RandomForestClassifier persisted under `backend/models/` |

Frontend assets live in `src/`. Backend, diagnostics, and ML assets reside under `backend/`.

---

## 3. Algorithms & Pipelines

### 3.1 Soil Health Flow
1. **Input normalization**: Nutrient, moisture, and sensor metadata are validated and scaled.
2. **Dual-write persistence**: Records are inserted into MySQL. If the DB is unreachable, the API automatically falls back to CSV so no submission is lost.
3. **Rule-based guidance**: Baseline heuristics produce immediate textual advice while the ML model (below) provides region-aware crop suggestions when available.

### 3.2 Crop Recommendation Model
- **Dataset**: `data/crop_recommendations.csv` tracks region, state, climate zone, rainfall/temperature ranges, humidity, soil profile, irrigation access, altitude, and drought/flood/wind risks. The label is `recommended_crop`.
- **Preprocessing**: `ColumnTransformer` + `OneHotEncoder(handle_unknown="ignore")` encode categorical dimensions while numeric bands pass through unchanged.
- **Model**: `RandomForestClassifier` (300 trees, max depth 12, `class_weight="balanced"`, seed 42). It handles mixed categorical inputs and remains interpretable for agronomists.
- **Training**: `python backend/train_crop_model.py` fits the pipeline, evaluates accuracy/classification report/confusion matrix, then saves artifacts to `backend/models/crop_recommender.pkl` with metrics JSON.

### 3.3 Diagnostics & Resilience
- `backend/debug_mysql.py` probes connectivity, schema readiness, and CSV backups.
- Startup hooks in `backend/app.py` log MySQL availability and sensor simulator status for fast troubleshooting.

---

## 4. Getting Started

### 4.1 Prerequisites
- Node.js 18+
- pnpm or npm (project uses `pnpm` by default — npm works too)
- Python 3.11+
- MySQL 8.x instance (local or remote)

### 4.2 Installation
```sh
git clone https://github.com/shantanushewale24/harit-samarth-app.git
cd harit-samarth-app

# Frontend deps
pnpm install   # or npm install

# Backend deps
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 4.3 Environment Variables (`backend/.env`)
```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=harit
MYSQL_PASSWORD=secret
MYSQL_DATABASE=harit_samarth
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
WEATHER_API_KEY=91c921b2103f4226b63110342250212
```

---

## 5. Running the Project

### Frontend
```sh
pnpm dev  # http://localhost:5173
```

### Backend
```sh
cd backend
.venv\Scripts\activate
python app.py
```

### Train / Update the Crop Model
```sh
cd backend
.venv\Scripts\activate
python train_crop_model.py
```
Artifacts are saved under `backend/models/`.

---

## 6. Repository Layout (Highlights)
```
├── src/                # React pages, components, hooks, integrations
├── backend/
│   ├── app.py          # Flask server + dual-write soil health API
│   ├── train_crop_model.py
│   ├── debug_mysql.py  # CLI diagnostics
│   └── models/         # Saved ML pipelines + metrics
├── data/
│   └── crop_recommendations.csv
└── supabase/           # Supabase config + edge functions
```

---

## 7. Deployment Notes
- Frontend bundles via `pnpm build` and can be hosted on Vercel, Netlify, or any static host.
- Backend targets environments with Python 3.11+, MySQL connectivity, and access to the trained model.
- Run `backend/debug_mysql.py` before releases to verify DB health and CSV backups.

---

## 8. Roadmap
1. Integrate live weather + satellite indices for dynamic inputs.
2. Expose the crop model through versioned API endpoints with caching.
3. Expand the dataset with yield history and subsidy eligibility tags.
