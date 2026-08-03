# BL-DCMS Android Application

## Project Overview

BL-DCMS (Railway Digital Checksheet Management System) — Android client. This document describes **only what is currently implemented** in `/opt/bldcms/Android`. It is the single source of truth for the Android app's architecture and must be read before any new module is implemented, and updated whenever the implementation changes.

### Purpose of the application

A field app for railway technicians to authenticate, and — in modules not yet built — fill and submit digital equipment checksheets that supervisors then review on the separate web dashboard. Today, the app implements authentication only (login → OTP → session restore); no checksheet functionality exists yet in the Android codebase.

### High-level architecture

```
Jetpack Compose UI
      │
ViewModel (Hilt-injected, StateFlow-driven)
      │
Repository interface (domain layer)
      │
Repository implementation (data layer)
      │
Retrofit (AuthApi) ── OkHttp (AuthInterceptor) ──► FastAPI backend
      │
DataStore (SessionPreferences) — local session persistence
```

### Technology stack

| Concern | Library / Version |
|---|---|
| UI | Jetpack Compose (BOM 2024.06.00), Material 3 |
| DI | Hilt 2.51.1 + KSP |
| Networking | Retrofit 2.9.0, OkHttp 4.12.0 (+ logging interceptor), kotlinx-serialization converter 1.0.0 |
| Serialization | kotlinx-serialization-json 1.7.3 |
| Local storage | AndroidX DataStore Preferences 1.1.0 |
| Navigation | Navigation Compose 2.8.0 |
| Language | Kotlin 2.0.21, JVM target 17 |
| Build | AGP 8.6.0, single Gradle module (`:app`) |

### Supported Android version

`minSdk 24`, `targetSdk 34`, `compileSdk 34` (`app/build.gradle.kts`).

### Project goals

Full workflow (per current product brief): technician login → OTP → JWT issued → JWT persisted → splash restores session → technician fills checksheets → data uploaded to backend → supervisors review via the web dashboard. **Only the login → OTP → JWT → session-restore portion is implemented today.**

---

## Architecture

### MVVM
Each screen has a `@HiltViewModel` exposing a single immutable `StateFlow<UiState>` (`LoginUiState`, `OtpUiState`, `SplashUiState`), mutated internally via a private `MutableStateFlow`. Chosen so Compose screens stay stateless/declarative — they `collectAsStateWithLifecycle()` and re-render, never holding business state themselves. `HomeScreen` is currently a static composable with no ViewModel (nothing to manage yet).

### Repository Pattern
Two repositories exist: `AuthRepository` (remote auth actions) and `SessionRepository` (local session persistence). Each is a `domain/repository` interface implemented by a `data/repository` class. This isolates ViewModels from Retrofit/DataStore specifics entirely — a ViewModel only ever depends on the interface, never the concrete implementation or the underlying transport. Chosen so the transport (Retrofit) or storage (DataStore) can be swapped or faked in tests without touching ViewModel code — this is exactly how `OtpViewModelTest` fakes both repositories today.

### Dependency Injection
Hilt, entirely `SingletonComponent`-scoped, three modules: `AppModule` (provides the `DataStore<Preferences>`), `NetworkModule` (provides `Json`, `OkHttpClient`, `Retrofit`, `AuthApi`, and binds `AuthRepository` via `@Provides`), `SessionModule` (binds `SessionRepository` via `@Binds`). Chosen for compile-time-verified, constructor-based injection with no service-locator boilerplate, and because a small single-activity app has no need for narrower scopes yet.

### Navigation
Single `NavHost` defined inline inside `MainActivity.kt` (`ChecksheetNavHost`), not a separate file. Chosen (implicitly, by what's actually wired up) to keep the composition root and the nav graph in one obviously-executed place — a second file, `navigation/AppNavHost.kt`, also defines a `NavHost` but is **never invoked from anywhere** (dead code; see Known Technical Debt).

### Networking
Retrofit + OkHttp, with kotlinx-serialization for JSON (not Moshi/Gson) to match the rest of the Kotlin-first stack and share the same `Json` instance's configuration (`ignoreUnknownKeys = true`, `coerceInputValues = true`) across encode/decode. An `AuthInterceptor` transparently attaches the bearer token to every request, so no repository or ViewModel ever constructs an `Authorization` header manually.

### Session Management
Jetpack DataStore (`Preferences`), wrapped by `SessionPreferences`, exposing `access_token`/`token_type` as `Flow<String?>`. Chosen over `SharedPreferences` for coroutine/Flow-native, type-safe, async-by-default reads/writes, consistent with the rest of the app's coroutine/Flow-based state management.

### Authentication
OTP-based, backend-driven (bcrypt password check → OTP issuance → OTP verification → JWT). The Android app never derives or validates the JWT itself — it treats the token as opaque, persists it, and lets the backend (`GET /auth/me`) be the arbiter of whether it's still valid. Chosen because the backend already implements this exact contract; the Android app's job is only to drive the two-step (password, then OTP) flow and store the resulting token.

---

## Folder Structure

```
com.checksheet.android
├── ChecksheetApplication.kt     — @HiltAndroidApp entry point, enables the DI graph
├── MainActivity.kt              — @AndroidEntryPoint single Activity; hosts ChecksheetNavHost inline
├── BuildConfig.kt                — hand-written file containing an unused `ApiConfig` object (dead code)
│
├── data/
│   ├── api/
│   │   └── AuthApi.kt            — Retrofit interface; the literal backend contract (3 endpoints)
│   ├── model/                    — kotlinx.serialization DTOs, one file each:
│   │   ├── LoginRequest.kt
│   │   ├── LoginResponse.kt
│   │   ├── OtpVerificationRequest.kt
│   │   ├── TokenResponse.kt
│   │   └── UserProfileResponse.kt
│   ├── network/
│   │   └── AuthInterceptor.kt    — OkHttp Interceptor; injects `Authorization: Bearer <token>`
│   ├── repository/               — concrete implementations of the domain interfaces
│   │   ├── AuthRepositoryImpl.kt
│   │   └── SessionRepositoryImpl.kt
│   └── session/
│       └── SessionPreferences.kt — DataStore wrapper; the only class that touches DataStore directly
│
├── domain/
│   └── repository/               — abstractions ViewModels depend on; no Android/Retrofit types
│       ├── AuthRepository.kt
│       └── SessionRepository.kt
│
├── di/
│   ├── AppModule.kt               — provides DataStore<Preferences>
│   ├── NetworkModule.kt           — provides Json/OkHttp/Retrofit/AuthApi/AuthRepository
│   └── SessionModule.kt           — binds SessionRepositoryImpl → SessionRepository
│
├── navigation/
│   └── AppNavHost.kt              — dead stub NavHost (unused — see Known Technical Debt)
│
├── theme/
│   └── Theme.kt                   — ChecksheetTheme: light/dark ColorScheme, default Typography
│
└── ui/
    ├── splash/  {SplashScreen.kt, SplashViewModel.kt}
    ├── login/   {LoginScreen.kt, LoginViewModel.kt}
    ├── otp/     {OtpScreen.kt, OtpViewModel.kt}
    └── home/    {HomeScreen.kt}    — static composable, no ViewModel yet
```

**Package responsibilities**, in one line each:
- `data.api` — declares exactly what HTTP calls exist; nothing else may call the backend directly.
- `data.model` — wire format DTOs; `@SerialName` maps to the backend's snake_case exactly.
- `data.network` — cross-cutting HTTP concerns (currently just auth-header injection).
- `data.repository` — translates domain calls into Retrofit/DataStore calls.
- `data.session` — the only class allowed to read/write DataStore directly.
- `domain.repository` — the contract ViewModels are written against; platform-agnostic.
- `di` — object graph wiring only; no business logic.
- `navigation` — intended home for nav graph code; currently superseded by inline code in `MainActivity`.
- `theme` — Compose Material 3 theming only.
- `ui.*` — one package per screen; each contains exactly a `Screen` composable and its `ViewModel`.

---

## Dependency Graph

```
Compose UI (Screen)
      │  collectAsStateWithLifecycle()
      ▼
ViewModel (@HiltViewModel, StateFlow<UiState>)
      │  constructor-injected domain interface
      ▼
Repository interface (domain.repository)
      │  implemented by
      ▼
Repository implementation (data.repository)
      │  calls
      ▼
AuthApi (Retrofit, data.api)  ──or──  SessionPreferences (DataStore, data.session)
      │
      ▼ (AuthApi only)
OkHttpClient (+ AuthInterceptor attaches Bearer token from SessionRepository)
      │
      ▼
FastAPI backend
      │
      ▼ (response)
Repository implementation → Repository interface → ViewModel → StateFlow emits new UiState → Compose recomposes
```

Hilt object graph (see §Architecture/DI): `AppModule` → `DataStore<Preferences>` → `SessionPreferences` → `SessionRepositoryImpl` → (`@Binds`) `SessionRepository`. `NetworkModule` → `Json`, `HttpLoggingInterceptor` → `OkHttpClient(+AuthInterceptor(SessionRepository))` → `Retrofit` → `AuthApi` → `AuthRepositoryImpl` → `AuthRepository`. Every ViewModel receives `AuthRepository` and/or `SessionRepository` by constructor injection — none reach into `di` directly.

---

## Navigation Graph

Defined in `MainActivity.kt` as `ChecksheetNavHost`, start destination `"splash"`.

```
splash
  │
  ├─ onNavigateToLogin ──► login          (popUpTo("splash"){inclusive=true}, launchSingleTop=true)
  └─ onNavigateToHome  ──► home           (popUpTo("splash"){inclusive=true}, launchSingleTop=true)

login
  └─ onOtpRequested(employeeId, password) ──► otp/{employeeId}/{urlEncodedPassword}

otp/{employeeId}/{password}
  └─ onVerificationSuccess ──► home        (popUpTo("login"){inclusive=false})

home   — terminal screen today; no further destinations exist in code
```

**Navigation rules actually implemented:**
- Splash always removes itself from the back stack when leaving (`inclusive = true`) — a user can never navigate back to Splash.
- The password is passed as a **route argument**, URL-encoded via `URLEncoder`/`URLDecoder`, from Login to OTP — required because the OTP screen's "Resend OTP" action re-submits the original password to `/mobile-auth/login`.
- Navigating from OTP to Home uses `popUpTo("login"){inclusive=false}` — this removes the OTP screen from the back stack but **keeps Login on it**, meaning a back-press from Home currently returns to the Login screen rather than exiting the app. This is a factual, observable behavior — not evaluated here as right or wrong, just documented as-is (see Known Technical Debt for whether this should be revisited).
- There is no route for Profile, Settings, Checksheet, or History yet — these are future modules, not yet present in the nav graph.

---

## Authentication Flow

```
Employee ID + Password entered on LoginScreen
      │
LoginViewModel.requestOtp()
      │  validates both fields non-empty
      ▼
AuthRepository.login(LoginRequest{employeeId, password, deviceType="ANDROID"})
      │
POST /mobile-auth/login
      │
      ▼
LoginResponse{requiresOtp, message}
      │  requiresOtp == true
      ▼
Navigate to OtpScreen (employeeId, password carried via route)
      │
User enters 6-digit OTP
      │
OtpViewModel.verifyOtp(employeeId)
      │  validates otp.length == 6
      ▼
AuthRepository.verifyOtp(OtpVerificationRequest{employeeId, otp, deviceType="ANDROID"})
      │
POST /mobile-auth/verify-otp
      │
      ▼
TokenResponse{accessToken, tokenType}
      │
SessionRepository.saveAccessToken(accessToken)
SessionRepository.saveTokenType(tokenType)
      │  (persisted to DataStore)
      ▼
Navigate to HomeScreen
```

**Error handling implemented** (both `LoginViewModel.requestOtp()` and `OtpViewModel.verifyOtp()`/`resendOtp()`): `HttpException` mapped by status code (401 → "Invalid Employee ID or Password" / "Invalid OTP", 429 → "Please wait before requesting another OTP." / "Too many attempts", 500 → generic server-error message, other → the exception's own message); `IOException` → "Cannot connect to server." / "Network error"; any other `Exception` → generic "Request failed" / "Verification failed". None of these paths touch `SessionRepository` — a failed login/OTP attempt never writes or clears session state.

**OTP resend + countdown** (already implemented, part of the OTP screen, not a future module): `OtpViewModel` starts a 30-second countdown coroutine on init; "Resend OTP" is disabled until it reaches zero; tapping it re-calls `AuthRepository.resendOtp()` (which is the same call as `login()` — the backend has no separate resend endpoint), clears the entered OTP, and restarts the countdown.

---

## Session Restoration

Implemented entirely in `SplashViewModel.checkSession()`, invoked once from `init {}`:

```
Read access token from SessionRepository.getAccessToken() (DataStore Flow, .firstOrNull())
      │
      ├─ null / blank ──► shouldNavigateToLogin = true ──► LoginScreen
      │
      └─ present
            │
            ▼
      AuthRepository.getUserProfile()   →  GET /auth/me  (Authorization header via AuthInterceptor)
            │
      ┌─────┼──────────────────┬───────────────────────┐
      ▼                        ▼                        ▼
   success                 HttpException              IOException
   (any 2xx)               (e.g. 401 — invalid/        (network unreachable)
      │                     revoked session)                │
      ▼                        ▼                        ▼
shouldNavigateToHome=true  sessionRepository.clearSession()  showRetry = true
                           shouldNavigateToLogin = true       (session is NOT cleared;
                                                                user can tap "Retry" to
                                                                re-run checkSession())
```

A bare `Exception` (neither `HttpException` nor `IOException`) is also treated as invalid-session: session is cleared and the user is routed to Login. The key distinction actually encoded in the code: **only a definite server rejection (`HttpException`) or an unexpected error clears the local session; a network failure (`IOException`) does not** — the user is offered a retry instead of being logged out.

---

## Backend Contracts

These are the **only** endpoints the Android app currently calls, as declared in `data/api/AuthApi.kt`. Nothing beyond this list exists in the codebase — no other endpoint may be assumed or invented.

| Method | URL | Request body | Response body | Auth required |
|---|---|---|---|---|
| POST | `/mobile-auth/login` | `LoginRequest` | `LoginResponse` | No |
| POST | `/mobile-auth/verify-otp` | `OtpVerificationRequest` | `TokenResponse` | No |
| GET | `/auth/me` | — | `UserProfileResponse` | Yes (Bearer JWT, via `AuthInterceptor`) |

Base URL: `BuildConfig.API_BASE_URL`, a Gradle `buildConfigField` sourced from `local.properties` → `API_BASE_URL` (falls back to `http://YOUR_SERVER_IP:8080/` if the property is absent — see `app/build.gradle.kts`). Note the separate, dead `BuildConfig.kt`/`ApiConfig.API_BASE_URL = "http://10.0.2.2:8000/"` is **not** used anywhere (see Known Technical Debt) — the real base URL always comes from the generated `BuildConfig` class.

---

## Data Models

All in `data/model/`, all `@Serializable`, all field names mapped to the backend's snake_case via `@SerialName`.

**`LoginRequest`** — sent to `/mobile-auth/login`
| Field | Type | Wire name | Notes |
|---|---|---|---|
| `employeeId` | String | `employee_id` | required |
| `password` | String | `password` | required |
| `deviceType` | String | `device_type` | defaults `"ANDROID"`, always sent as such today |
| `deviceName` | String? | `device_name` | optional, never populated by current UI |
| `ipAddress` | String? | `ip_address` | optional, never populated by current UI |
| `userAgent` | String? | `user_agent` | optional, never populated by current UI |

**`LoginResponse`** — returned by `/mobile-auth/login`
| Field | Type | Wire name |
|---|---|---|
| `requiresOtp` | Boolean | `requires_otp` |
| `message` | String | `message` |

**`OtpVerificationRequest`** — sent to `/mobile-auth/verify-otp`
| Field | Type | Wire name | Notes |
|---|---|---|---|
| `employeeId` | String | `employee_id` | required |
| `otp` | String | `otp` | required, always 6 digits by the time it's sent (enforced client-side) |
| `deviceType` | String | `device_type` | defaults `"ANDROID"` |
| `deviceName` | String? | `device_name` | optional, unpopulated |
| `ipAddress` | String? | `ip_address` | optional, unpopulated |
| `userAgent` | String? | `user_agent` | optional, unpopulated |

**`TokenResponse`** — returned by `/mobile-auth/verify-otp`
| Field | Type | Wire name |
|---|---|---|
| `accessToken` | String | `access_token` |
| `tokenType` | String | `token_type` |

**`UserProfileResponse`** — returned by `/auth/me`
| Field | Type | Wire name | Notes |
|---|---|---|---|
| `id` | Int | `id` | |
| `employeeId` | String | `employee_id` | |
| `name` | String | `name` | |
| `mobile` | String? | `mobile` | optional |
| `email` | String? | `email` | optional |
| `role` | String? | `role` | optional; not yet used for any client-side gating |
| `sectionId` | Int? | `section_id` | optional |
| `sectionName` | String? | `section_name` | optional |

---

## Repository Layer

### `AuthRepository` (domain) / `AuthRepositoryImpl` (data)
- **Responsibilities**: all remote authentication actions.
- **Methods**: `suspend fun login(request: LoginRequest): LoginResponse`, `suspend fun resendOtp(request: LoginRequest): LoginResponse` (aliases `login` — no dedicated backend endpoint), `suspend fun verifyOtp(request: OtpVerificationRequest): TokenResponse`, `suspend fun getUserProfile(): UserProfileResponse`.
- **Dependencies**: `AuthApi` only.
- **Future extensions**: any new authenticated endpoint (profile update, logout, etc.) should be added here only once the corresponding backend route is confirmed to exist — never speculatively.

### `SessionRepository` (domain) / `SessionRepositoryImpl` (data)
- **Responsibilities**: local session token persistence and derived session-validity state.
- **Methods**: `getAccessToken(): Flow<String?>`, `suspend fun saveAccessToken(token: String)`, `suspend fun saveTokenType(type: String)`, `getTokenType(): Flow<String?>`, `suspend fun clearSession()`, `hasValidSession(): Flow<Boolean>` (derived via `combine` of the token+type flows — true iff both are non-blank).
- **Dependencies**: `SessionPreferences` only.
- **Future extensions**: this is the natural home for a refresh-token field/method if the backend ever exposes token refresh; currently no such backend endpoint exists, so none has been added.

---

## ViewModels

### `LoginViewModel`
- **Responsibilities**: own the login form's state; trigger the OTP request.
- **StateFlow**: `LoginUiState(employeeId, password, isLoading, errorMessage, otpRequested, requestedEmployeeId)`.
- **Events**: `onEmployeeIdChanged`, `onPasswordChanged`, `requestOtp()`.
- **Navigation responsibility**: none directly — it only flips `otpRequested`/`requestedEmployeeId`; `LoginScreen` observes this and invokes the `onOtpRequested` callback passed in from the NavHost.
- **Validation**: both `employeeId` (trimmed) and `password` must be non-empty, or a local error message is set without calling the network.

### `OtpViewModel`
- **Responsibilities**: own OTP entry, the 30-second resend countdown, OTP verification, and persisting the resulting token.
- **StateFlow**: `OtpUiState(otp, isLoading, errorMessage, verificationSuccess, countdownSeconds=30, canResend, resendSuccess)`.
- **Events**: `onOtpChanged` (filters to digits, truncates to 6), `resendOtp(employeeId, password)`, `verifyOtp(employeeId)`.
- **Navigation responsibility**: none directly — flips `verificationSuccess`; `OtpScreen`'s `LaunchedEffect` invokes `onVerificationSuccess` in response.
- **Validation**: `verifyOtp` requires exactly 6 digits before calling the network; the "Verify" button is also disabled in the UI until then.

### `SplashViewModel`
- **Responsibilities**: decide, once, whether the app opens to Home or Login.
- **StateFlow**: `SplashUiState(isLoading=true, errorMessage, showRetry, shouldNavigateToLogin, shouldNavigateToHome)`.
- **Events**: `checkSession()` (also called automatically from `init {}`).
- **Navigation responsibility**: none directly — flips `shouldNavigateToLogin`/`shouldNavigateToHome`; `SplashScreen` reacts to these booleans and invokes the corresponding callback.
- **Validation**: none (no user input on this screen).

**Common pattern across all three ViewModels**: no ViewModel ever calls `NavController` directly, and no ViewModel calls Retrofit or DataStore directly — only through the injected repository interfaces. This is the rule to preserve for every future ViewModel.

---

## Session Layer

- **`SessionRepository`** — the only interface ViewModels/interceptors are allowed to depend on for session state (see Repository Layer above).
- **`SessionPreferences`** — the only class that touches `DataStore<Preferences>` directly; defines two keys, `stringPreferencesKey("access_token")` and `stringPreferencesKey("token_type")`; exposes them as `Flow`s and provides `save*`/`clearSession` suspend functions (`clearSession` removes both keys).
- **`AuthInterceptor`** (OkHttp `Interceptor`) — on every outgoing request, synchronously reads `sessionRepository.getAccessToken().firstOrNull()` via `runBlocking`; if a token is present, adds `Authorization: Bearer <token>` to the request; if absent, the request proceeds unmodified (relevant for the two pre-auth endpoints, `/mobile-auth/login` and `/mobile-auth/verify-otp`, which don't need — and today don't have — a token yet).
- **Token storage**: DataStore Preferences file `"checksheet_preferences"` (created via `PreferenceDataStoreFactory` in `AppModule`), storing only the raw access token string and its token type (`"bearer"`); no expiry timestamp, no refresh token is stored (the backend does not currently issue one to this client — see Known Technical Debt).
- **Authorization header injection**: happens exclusively inside `AuthInterceptor`; no repository, ViewModel, or Retrofit interface method ever sets this header manually.

---

## Coding Standards

Rules already followed by the existing code, to be maintained for every future module:

- Never navigate inside repositories or ViewModels — navigation is decided by boolean/event fields in `UiState`, and executed only inside the Composable via `LaunchedEffect`/direct callback invocation.
- Never call Retrofit (`AuthApi`) or DataStore (`SessionPreferences`) directly from UI or ViewModels — always go through the `domain.repository` interfaces.
- ViewModels expose a single immutable `StateFlow<UiState>` (`.asStateFlow()`), never a mutable one, and never individual loose fields.
- Repositories return the DTOs defined in `data.model` (there is no separate "domain object" translation layer today — DTOs are used directly as the domain model, since they are already 1:1 with what the UI needs).
- Never duplicate or invent backend contracts — `AuthApi` must exactly mirror the backend's actual routes and payload shapes; new fields/endpoints are added only after confirming the backend already supports them.
- Keep UI stateless — screens read `UiState` and emit events; they hold no business state of their own beyond ephemeral local UI state (e.g. `passwordVisible` in `LoginScreen`).
- Prefer constructor injection (`@Inject constructor` / `@HiltViewModel`) everywhere; no field injection, no service locators.
- Never hardcode base URLs in code that's actually used — `BuildConfig.API_BASE_URL` (Gradle-generated, sourced from `local.properties`) is the only base URL consumed by `NetworkModule`.
- Never bypass `SessionRepository` — all token reads/writes/clears go through it, never direct `DataStore` access from outside `data.session`.

---

## Completed Modules

- [x] Module 1 — Project architecture (package structure, Hilt setup, Gradle/build config)
- [x] Module 2 — Networking layer (`NetworkModule`, `AuthApi`, `AuthInterceptor`, OkHttp/Retrofit/kotlinx-serialization wiring)
- [x] Module 3 — Session / DataStore (`SessionPreferences`, `SessionRepository`/`Impl`, `SessionModule`)
- [x] Module 4 — Login screen (`LoginScreen`, `LoginViewModel`, calls `/mobile-auth/login`)
- [x] Module 5 — OTP verification (`OtpScreen`, `OtpViewModel`, calls `/mobile-auth/verify-otp`, includes resend + 30s countdown)
- [x] Module 6 — Splash / session restore (`SplashScreen`, `SplashViewModel`, calls `/auth/me`, retry-on-network-error handling)
- [ ] Module 7 — under development; scope not yet defined in this document (update this entry once scope is confirmed)

---

## Planned Modules

Scope and order to be confirmed before implementation; listed here only as a backlog, not as committed design:

- Logout (no backend endpoint currently exists for this — see Known Technical Debt; needs a decision before implementation)
- Profile screen (backend already returns enough via `GET /auth/me` — `UserProfileResponse` — to support a read-only profile view today)
- Settings screen
- Checksheet list / detail / creation (the largest planned module; depends on backend endpoints not yet inventoried for this document, since this document currently only covers the auth surface actually consumed by the Android app)
- Offline cache / sync for checksheet drafts
- Reports (mobile-side, if planned — the web Dashboard already has a Reports page against the same backend)
- Manual dark-mode toggle (today the app only follows the system's light/dark setting via `isSystemInDarkTheme()`, with no in-app override)

---

## Future Improvements

**Architecture**
- Introduce a shared 401/expired-session handling mechanism (e.g. an OkHttp `Authenticator`, or a small shared helper) before more authenticated endpoints are added, so each new repository doesn't reimplement the same "catch 401 → clear session → route to Login" logic independently.
- Decide whether DTOs should stay the domain model long-term (fine at current scale) or whether a real domain-model translation layer is warranted once more complex screens (e.g. checksheets) are added.

**Performance**
- None identified yet at this module count; revisit once network calls multiply beyond the current three endpoints.

**Security**
- Move the OTP-flow password (currently passed as a Compose Navigation route argument between Login and OTP) to a shared, ViewModel-scoped holder instead of the back stack/`SavedStateHandle`, if a security review flags this.
- Add a client-side token-expiry check (or a refresh flow) rather than relying solely on reactive 401 detection, if/when the backend exposes one.

**Testing**
- Add unit tests for `LoginViewModel` and `SplashViewModel` (only `OtpViewModel` and one serialization test currently exist).
- Add a test for `AuthInterceptor` (currently untested).

**UI**
- No manual theme toggle exists; only automatic system light/dark following.

---

## Known Technical Debt

| Item | Why it exists | Risk | Future solution |
|---|---|---|---|
| `navigation/AppNavHost.kt` is dead code — a stub `NavHost` with plain `Text("Splash")`/`Text("Login")`/`Text("Home")` composables, never invoked | Early scaffolding (likely Module 1), superseded when the real nav graph was written inline in `MainActivity.kt` | Low — no runtime effect, but confusing for onboarding; a reader may assume it's the active nav graph | Delete once a cleanup pass is authorized |
| `BuildConfig.kt` contains an unused hand-written `object ApiConfig` with a hardcoded emulator URL (`http://10.0.2.2:8000/`) | Likely an early placeholder before `BuildConfig.API_BASE_URL` (Gradle-generated) was wired up | Low today (unused), but its name collides conceptually with the real generated `BuildConfig` class sitting alongside it | Delete once confirmed unused; rename if ever revived |
| Password passed as a Compose Navigation route argument (URL-encoded) between Login and OTP screens | Needed so the OTP screen's "Resend" action can resubmit the original password to `/mobile-auth/login` (no session/holder object exists yet to carry it another way) | Low-moderate — transient exposure in the back stack / process-death state restoration | Introduce a small shared, ViewModel-scoped or SavedStateHandle-backed holder if a security review requires it |
| No client-side JWT expiry tracking; only reactive 401 detection on the one authenticated call that exists (`/auth/me` from Splash) | Backend contract offers no refresh token to this client today | As more authenticated calls are added, users may hit a stale-token 401 mid-task with no graceful pre-emptive handling | Add shared 401-handling (see Future Improvements) once more authenticated endpoints exist; revisit if backend adds refresh-token support |
| Back navigation from Home currently returns to Login (Login is not popped when navigating Otp→Home, only `inclusive=false`) | Byproduct of the current `popUpTo` configuration | Low — functional, but may not match intended UX (unclear whether "back to Login from Home" is desired) | Confirm intended behavior with product owner; adjust `popUpTo` if Login should be excluded from the back stack after successful auth |

---

## Change Log

| Date | Change |
|---|---|
| 2026-07-08 | Initial version of this document created. Captures Modules 1–6 as implemented (project architecture, networking, session/DataStore, login, OTP verification incl. resend/countdown, splash/session-restore). Module 7 noted as in progress with scope not yet defined. Documents only the three backend endpoints actually consumed (`/mobile-auth/login`, `/mobile-auth/verify-otp`, `/auth/me`) and the five DTOs actually present in `data/model/`. |

**Maintenance rule**: before implementing any new module, read this document first; after implementing it, update the relevant sections (Folder Structure, Dependency/Navigation Graphs, Backend Contracts, Data Models, Repository/ViewModel sections, Completed/Planned Modules, and this Change Log) in the same session — this document must never fall out of sync with the source code.
