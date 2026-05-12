# Full-Stack Architecture Plan — Deal Verdict Wizard Platform

**Source requirement:** `_requirements/20260511-requirement.md`
**Current state:** Pure Streamlit app (`rental_platform/` package) with in-memory session state, no persistence, no authentication, no API layer.
**Target state:** Multi-layer full-stack system — FastAPI backend, React frontend with Redux Toolkit, SQLite/SQLAlchemy persistence, JWT authentication, provider-based auth architecture.

---

## Target Architecture

```
Browser (React + Redux Toolkit)
         ↓
  API Service Layer (axios + interceptors)
         ↓
  FastAPI Backend  (/api/v1/...)
         ↓
  Service Layer  (ported from rental_platform/services/)
         ↓
  Repository Layer  (data access abstraction)
         ↓
  SQLModel + Alembic ORM
         ↓
  SQLite (dev) → PostgreSQL (production)
```

---

## New Repository Structure

```
rental-application/
├── backend/
│   ├── app/
│   │   ├── main.py                    ← FastAPI app factory
│   │   ├── config.py                  ← env-based settings (pydantic-settings)
│   │   ├── database.py                ← engine + session factory
│   │   ├── auth/
│   │   │   ├── providers/
│   │   │   │   ├── base.py            ← AuthProvider abstract class
│   │   │   │   ├── password.py        ← bcrypt/argon2 username+password
│   │   │   │   └── oauth_google.py    ← (Phase 5 placeholder)
│   │   │   ├── dependencies.py        ← get_current_user FastAPI dep
│   │   │   ├── jwt.py                 ← token creation / verification
│   │   │   └── router.py              ← /api/v1/auth endpoints
│   │   ├── models/
│   │   │   ├── db/                    ← SQLModel table models
│   │   │   │   ├── user.py
│   │   │   │   ├── auth_provider.py
│   │   │   │   ├── deal.py
│   │   │   │   ├── deal_verdict.py
│   │   │   │   └── report.py
│   │   │   └── schemas/               ← Pydantic request/response models
│   │   │       ├── auth.py
│   │   │       ├── deal.py
│   │   │       └── user.py
│   │   ├── repositories/
│   │   │   ├── base.py                ← Generic CRUD repository
│   │   │   ├── user_repo.py
│   │   │   └── deal_repo.py
│   │   ├── services/                  ← Ported from rental_platform/services/
│   │   │   ├── financing_service.py
│   │   │   ├── underwriting_service.py
│   │   │   ├── verdict_service.py
│   │   │   ├── proforma_service.py
│   │   │   ├── brrrr_service.py
│   │   │   ├── tax_service.py
│   │   │   ├── profit_first_service.py
│   │   │   └── crm_service.py
│   │   ├── routers/
│   │   │   ├── v1/
│   │   │   │   ├── deals.py           ← /api/v1/deals
│   │   │   │   ├── calculations.py    ← /api/v1/calculations
│   │   │   │   ├── reports.py         ← /api/v1/reports
│   │   │   │   └── users.py           ← /api/v1/users
│   │   │   └── router.py              ← assembles all v1 routers
│   │   └── middleware/
│   │       └── error_handler.py       ← global exception → structured response
│   ├── alembic/                       ← database migrations
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_deals.py
│   │   └── test_calculations.py
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── store/                     ← Redux Toolkit store
│   │   │   ├── index.ts
│   │   │   ├── authSlice.ts
│   │   │   ├── dealSlice.ts
│   │   │   └── uiSlice.ts
│   │   ├── services/                  ← axios API service layer
│   │   │   ├── api.ts                 ← axios instance + interceptors
│   │   │   ├── authService.ts
│   │   │   ├── dealService.ts
│   │   │   └── calculationService.ts
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   ├── wizard/
│   │   │   │   ├── WizardShell.tsx
│   │   │   │   ├── steps/
│   │   │   │   │   ├── PropertyStep.tsx
│   │   │   │   │   ├── RentStep.tsx
│   │   │   │   │   ├── FinancingStep.tsx
│   │   │   │   │   ├── ExpensesStep.tsx
│   │   │   │   │   └── VerdictStep.tsx
│   │   │   └── dashboard/
│   │   │       └── DealList.tsx
│   │   └── pages/
│   │       ├── LoginPage.tsx
│   │       ├── DashboardPage.tsx
│   │       └── WizardPage.tsx
│   ├── package.json
│   └── vite.config.ts
├── rental_platform/                   ← kept; Streamlit UI bridges Phase 1-2
├── app.py                             ← Streamlit entry (retained until Phase 4)
└── _plan/, _spec/, _requirements/     ← unchanged
```

---

## Phase 1 — Backend Foundation

**Goal:** Establish the FastAPI project, ORM layer, database, and migration tooling.
**Deliverables:** Running FastAPI server with `/health` endpoint, first Alembic migration, tested repository layer.

### 1.1 Project scaffold

- Create `backend/` directory.
- Set up Python virtual environment (Python 3.11+) separate from the Streamlit venv.
- `backend/requirements.txt`:
  - `fastapi`, `uvicorn[standard]`
  - `sqlmodel` (bundles SQLAlchemy 2 + Pydantic v2)
  - `alembic`
  - `pydantic-settings`
  - `pytest`, `httpx` (for API tests)

### 1.2 Configuration (`backend/app/config.py`)

- Use `pydantic-settings` `BaseSettings` to load from `.env`.
- Key settings: `DATABASE_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `ENVIRONMENT`.
- Provide `.env.example` for local onboarding.

### 1.3 Database models — `backend/app/models/db/`

All models use `SQLModel` with `table=True`. Core tables:

- **`User`**: `id` (UUID), `email`, `display_name`, `is_active`, `created_at`
- **`AuthProvider`**: `id`, `user_id` (FK), `provider` (enum: `password`, `google`, `microsoft`), `provider_user_id`, `hashed_credential` (nullable — only for password provider)
- **`Deal`**: `id` (UUID), `user_id` (FK), `address`, `asset_type`, `status`, `created_at`, `updated_at`, `deal_data` (JSON blob — stores full DealProfile payload)
- **`DealVerdict`**: `id`, `deal_id` (FK), `verdict_status`, `monthly_cash_flow`, `dscr`, `cap_rate`, `total_cash_required`, `computed_at`
- **`Report`**: `id`, `user_id` (FK), `deal_id` (FK), `report_type`, `payload` (JSON), `generated_at`

The `deal_data` JSON column stores the full `DealProfile` dataclass payload from the existing `rental_platform/models/domain.py`, enabling zero-breaking-change persistence while the new frontend is built.

### 1.4 Repository layer — `backend/app/repositories/`

- `BaseRepository[T]`: generic typed class with `create`, `get_by_id`, `list_for_user`, `update`, `delete`.
- `UserRepository(BaseRepository[User])`: adds `get_by_email`.
- `DealRepository(BaseRepository[Deal])`: adds `list_by_user_id`, `get_with_verdicts`.
- All repositories receive a `db: Session` dependency-injected from FastAPI.

### 1.5 Alembic

- `alembic init alembic` inside `backend/`.
- Configure `env.py` to import `SQLModel.metadata`.
- Initial migration: creates all tables in § 1.3.

### 1.6 FastAPI app factory (`backend/app/main.py`)

```python
app = FastAPI(title="Rental Platform API", version="1.0.0")
app.include_router(api_v1_router, prefix="/api/v1")
# /health endpoint
# CORS middleware (localhost:3000 during dev)
# Global exception handler → structured JSON errors
```

### 1.7 Phase 1 tests

- `test_database.py`: creates in-memory SQLite, verifies all models create/migrate cleanly.
- `test_repositories.py`: CRUD round-trip for User and Deal via `TestClient` + test DB.

---

## Phase 2 — Authentication & User Management

**Goal:** Secure login with JWT, provider-based auth architecture, user isolation enforced at the API layer.
**Deliverables:** `/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/auth/refresh`, `get_current_user` dependency used on all protected routes.

### 2.1 Provider abstraction (`backend/app/auth/providers/base.py`)

```python
class AuthProvider(ABC):
    provider_name: str

    @abstractmethod
    def verify_credential(self, credential: str, stored: str) -> bool: ...

    @abstractmethod
    def hash_credential(self, credential: str) -> str: ...
```

- `PasswordProvider`: implements with `passlib[bcrypt]` or `argon2-cffi`. Configurable via `AUTH_HASH_ALGORITHM` env var.
- Future providers (`GoogleOAuthProvider`, `MicrosoftOAuthProvider`) implement the same interface; adding one requires only a new file + config entry — no changes to auth middleware.

### 2.2 JWT layer (`backend/app/auth/jwt.py`)

- `create_access_token(user_id, expires_delta)` → signed HS256 JWT.
- `create_refresh_token(user_id)` → longer-lived token.
- `decode_token(token)` → `TokenPayload` or raises `HTTPException 401`.
- Uses `python-jose[cryptography]`.

### 2.3 Auth router (`/api/v1/auth`)

| Endpoint | Method | Description |
|---|---|---|
| `/auth/register` | POST | Creates User + AuthProvider(password) row |
| `/auth/login` | POST | Verifies credential, returns access + refresh tokens |
| `/auth/refresh` | POST | Accepts refresh token, returns new access token |
| `/auth/logout` | POST | Invalidates refresh token (token denylist in DB or cache) |
| `/auth/me` | GET | Returns authenticated user profile |

### 2.4 `get_current_user` dependency

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User: ...
```

All non-auth endpoints use `current_user: User = Depends(get_current_user)`. Authorization checks (e.g., `deal.user_id == current_user.id`) are enforced inside routers or repositories — never only on the frontend.

### 2.5 Security requirements

- Passwords are never stored. Only the `hashed_credential` column is persisted.
- JWTs never contain sensitive data — only `user_id` and expiry.
- `SECRET_KEY` loaded exclusively from environment; never hardcoded.
- Refresh token stored in the `AuthProvider` row or a dedicated `RefreshToken` table with expiry + revocation flag.

### 2.6 Phase 2 tests

- `test_auth.py`: register → login → get protected resource → refresh → logout cycle.
- Negative cases: wrong password, expired token, reused refresh token.

---

## Phase 3 — Business Logic API

**Goal:** Expose the existing `rental_platform/services/` logic via versioned REST endpoints. Deals are saved to the database and scoped to the authenticated user.
**Deliverables:** Full `/api/v1/deals` CRUD + `/api/v1/calculations` compute-only endpoints.

### 3.1 Service layer migration

The existing service modules are **pure Python functions with no Streamlit dependency** and can be imported directly into the FastAPI backend:

- Copy `rental_platform/services/*.py` → `backend/app/services/*.py`
- Remove Streamlit session references (none exist — services are already clean)
- Services remain stateless functions; the API layer handles persistence

### 3.2 Deals router (`/api/v1/deals`)

| Endpoint | Method | Description |
|---|---|---|
| `/deals` | GET | List all deals for the authenticated user |
| `/deals` | POST | Create a new deal (persists `deal_data` JSON) |
| `/deals/{deal_id}` | GET | Get a single deal (ownership check enforced) |
| `/deals/{deal_id}` | PATCH | Update deal fields |
| `/deals/{deal_id}` | DELETE | Delete deal (soft-delete via `status = "deleted"`) |
| `/deals/{deal_id}/verdict` | POST | Compute + persist a verdict snapshot |
| `/deals/{deal_id}/verdicts` | GET | List historical verdicts for a deal |

All endpoints require `current_user`. `DealRepository.get_by_id` raises `403` if `deal.user_id != current_user.id`.

### 3.3 Calculations router (`/api/v1/calculations`)

Stateless compute endpoints — no persistence, no auth required (or optionally authed):

| Endpoint | Method | Description |
|---|---|---|
| `/calculations/verdict` | POST | Accepts full DealProfile payload, returns VerdictOutputs |
| `/calculations/proforma` | POST | Returns multi-year proforma table |
| `/calculations/financing` | POST | Returns loan amount, payment, DSCR |
| `/calculations/brrrr` | POST | Returns BRRRR equity/refinance metrics |
| `/calculations/tax` | POST | Returns depreciation schedule |
| `/calculations/profit-first` | POST | Returns cash allocation blueprint |

Request/response schemas use Pydantic models mirroring the existing dataclasses in `rental_platform/models/domain.py`.

### 3.4 Reports router (`/api/v1/reports`)

| Endpoint | Method | Description |
|---|---|---|
| `/reports` | GET | All reports for authenticated user |
| `/reports/{report_id}` | GET | Single report |
| `/deals/{deal_id}/reports` | POST | Generate + persist a deal summary report |

### 3.5 Response model standardisation

All responses follow:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

Errors:
```json
{
  "success": false,
  "data": null,
  "error": { "code": "DEAL_NOT_FOUND", "message": "...", "detail": [...] }
}
```

### 3.6 OpenAPI documentation

FastAPI auto-generates `/docs` (Swagger UI) and `/redoc`. Add operation IDs and descriptions to all routes for clean SDK generation.

### 3.7 Phase 3 tests

- `test_deals.py`: authenticated CRUD, ownership enforcement (user A cannot access user B's deal).
- `test_calculations.py`: each calculation endpoint with known inputs → expected outputs matched against existing pytest fixtures.

---

## Phase 4 — Frontend (React + Redux Toolkit)

**Goal:** Replace the Streamlit UI with a React SPA that communicates exclusively through the API layer.
**Deliverables:** Fully functional Deal Verdict Wizard, Dashboard, and Deal Report pages. Streamlit app retired.

### 4.1 Project scaffold

- `frontend/` initialised with Vite + React + TypeScript.
- Key dependencies:
  - `@reduxjs/toolkit`, `react-redux`
  - `axios`
  - `react-router-dom` v6
  - `react-hook-form` + `zod` (form validation)
  - `recharts` or `chart.js` (metrics visualisation)
  - `tailwindcss` (styling)

### 4.2 Redux store (`frontend/src/store/`)

- **`authSlice`**: `{ user, accessToken, refreshToken, isAuthenticated }`. Actions: `loginSuccess`, `logout`, `tokenRefreshed`.
- **`dealSlice`**: `{ deals[], activeDeal, wizardDraft, status }`. Actions: `loadDeals`, `saveDeal`, `updateWizardDraft`, `computeVerdict`.
- **`uiSlice`**: `{ wizardStep, notifications, loadingKeys }`.

The wizard draft (`wizardDraft`) in Redux replaces the Streamlit session state. All five wizard steps read from and write to this single Redux state slice.

### 4.3 API service layer (`frontend/src/services/`)

- `api.ts`: axios instance with `baseURL = /api/v1`. Request interceptor attaches `Authorization: Bearer <token>`. Response interceptor handles 401 → token refresh → retry.
- `authService.ts`: `login()`, `register()`, `refresh()`, `logout()`.
- `dealService.ts`: `listDeals()`, `createDeal()`, `updateDeal()`, `deleteDeal()`, `computeVerdict()`.
- `calculationService.ts`: thin wrappers around the calculation endpoints.

**UI components never call axios directly.** They dispatch Redux actions; the action thunks call service functions.

### 4.4 Authentication flow

1. User lands → `ProtectedRoute` checks `isAuthenticated` in Redux.
2. Not authenticated → redirect to `/login`.
3. `LoginForm` dispatches `loginThunk(credentials)` → `authService.login()` → stores tokens in Redux (access token in memory, refresh token in `httpOnly` cookie if backend supports it).
4. Token refresh: interceptor transparently retries failed requests after refreshing.

### 4.5 Deal Verdict Wizard

The 5-step wizard mirrors the existing Streamlit workflow but is fully client-side:

- Each step reads/writes `wizardDraft` in Redux.
- "Continue" button dispatches `updateWizardDraft(stepData)` + calls `calculationService.computeVerdict(draft)` to update the Live Verdict Preview.
- "Save Deal" button dispatches `saveDealThunk(wizardDraft)` → `dealService.createDeal()` or `updateDeal()`.
- Verdict step renders the final computed outputs fetched from `/calculations/verdict`.

### 4.6 Dashboard & Reports

- `DashboardPage` dispatches `loadDealsThunk()` on mount → renders `DealList` from Redux state.
- Deal cards show address, verdict status, last updated timestamp.
- Clicking a deal loads it into Redux and navigates to the wizard (pre-filled).
- `ReportsPage` fetches and renders saved verdicts and historical analyses per deal.

### 4.7 Phase 4 tests

- Component tests: `@testing-library/react` + `jest` for each wizard step.
- Redux slice unit tests: each action/thunk in isolation with mocked axios.
- End-to-end: Playwright or Cypress — login → fill wizard → save deal → see on dashboard.

---

## Phase 5 — Security Hardening & OAuth Readiness

**Goal:** Production-ready security posture, extensible auth, observability hooks.
**Deliverables:** OAuth provider scaffold, rate limiting, structured logging, input sanitisation, CORS lock-down.

### 5.1 OAuth scaffolding

- `GoogleOAuthProvider(AuthProvider)` and `MicrosoftOAuthProvider(AuthProvider)` created as stubs.
- `/api/v1/auth/oauth/{provider}/redirect` and `/api/v1/auth/oauth/{provider}/callback` endpoints added.
- `AuthProvider` DB row links an OAuth identity to a `User` — one user can have multiple linked providers.
- No UI changes required in Phase 4 beyond adding "Sign in with Google" buttons.

### 5.2 Rate limiting & abuse protection

- `slowapi` middleware on auth endpoints (`/auth/login`, `/auth/register`).
- Failed login attempts tracked in `AuthProvider` row; account lock after N failures.

### 5.3 Input validation & security

- All API payloads validated by Pydantic; unknown fields rejected.
- SQLModel ORM protects against SQL injection by design (no raw SQL).
- CORS restricted to approved origins via `ALLOWED_ORIGINS` env var.
- Sensitive fields (`hashed_credential`) excluded from all response schemas using Pydantic `exclude`.

### 5.4 Structured logging

- `structlog` or Python `logging` with JSON formatter.
- Every request logged with: `request_id`, `user_id` (if auth), `method`, `path`, `status_code`, `duration_ms`.
- Errors include stack trace in structured format.

### 5.5 RBAC scaffold (future-ready)

- `User.role` column (`owner`, `viewer`) added in migration.
- `require_role("owner")` dependency created but not yet enforced on endpoints.
- Team collaboration (multiple users per deal) designed as a future `DealMembership` join table.

---

## Phase Dependencies & Order

```
Phase 1 (Backend Foundation)
    → Phase 2 (Auth) — requires DB models and repository layer
        → Phase 3 (Business API) — requires auth dependency + DB
            → Phase 4 (Frontend) — requires complete API contract
                → Phase 5 (Hardening) — can partially parallel Phase 4
```

The existing Streamlit app remains fully operational throughout Phases 1–3. It is retired only when Phase 4 frontend reaches feature parity.

---

## Technology Decisions

| Layer | Choice | Rationale |
|---|---|---|
| Backend framework | FastAPI | Async, type-safe, OpenAPI auto-docs, Python ecosystem match |
| ORM | SQLModel | Combines SQLAlchemy 2 + Pydantic v2 in one model; avoids duplication |
| Migrations | Alembic | Standard SQLAlchemy migration tool; PostgreSQL-ready |
| Password hashing | passlib[bcrypt] | Industry standard; argon2 configurable via provider |
| JWT | python-jose | Lightweight, widely used with FastAPI |
| Frontend | React + TypeScript | Larger ecosystem vs Vue; strong typing for complex wizard state |
| State management | Redux Toolkit | Mature, predictable; async thunks fit API call pattern |
| Form handling | react-hook-form + zod | Performant, schema-validated forms aligned with Pydantic schemas |
| Styling | Tailwind CSS | Utility-first; no component-library lock-in |
| Build tool | Vite | Fast dev server, modern ESM bundling |
| E2E testing | Playwright | Cross-browser, reliable async support |

---

## Migration Strategy for Existing Services

The existing `rental_platform/services/` modules (`financing_service`, `underwriting_service`, `verdict_service`, `proforma_service`, etc.) contain pure Python business logic with **no Streamlit dependency**. Migration path:

1. Copy files to `backend/app/services/` — zero refactoring required.
2. Existing `rental_platform/models/domain.py` dataclasses become the canonical payload format for the `/calculations/*` endpoints.
3. Pydantic schemas in `backend/app/models/schemas/` are generated to mirror the dataclasses for request/response serialisation.
4. Existing `tests/` suite continues to pass throughout — the service logic is not modified, only wrapped by the API.

---

## Non-Functional Acceptance Criteria

- All API endpoints return within 500ms for CRUD operations in local development.
- Password hashing uses work factor ≥ 12 (bcrypt) or equivalent.
- No access token or password hash appears in any application log.
- `pytest tests/` (existing) continues to pass green throughout all phases.
- Backend test coverage for auth and deal endpoints ≥ 80%.
- Alembic migrations are reversible (all have `downgrade` implemented).
