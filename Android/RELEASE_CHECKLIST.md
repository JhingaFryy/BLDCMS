# BL-DCMS Android — Release Checklist

This document covers how to build, sign, and install the app, plus the checks to run through
before shipping a release. It reflects the app as of Module 22 (Production Hardening).

## 1. Prerequisites

- JDK 17
- Android SDK (this project's `local.properties` currently points `sdk.dir` at
  `CHANGE_ME_PATH_TO_ANDROID_SDK`)
- A running instance of the backend in `/opt/bldcms/Backend` reachable from the device/
  emulator (see "Required backend version" below)

## 2. Building a Debug APK

```bash
cd /opt/bldcms/Android
./gradlew assembleDebug
```

Output: `app/build/outputs/apk/debug/app-debug.apk` — signed automatically with the Android debug
keystore, installable directly with `adb install`.

## 3. Changing `API_BASE_URL`

The backend URL is **not hardcoded** — it's injected at build time via `BuildConfig.API_BASE_URL`,
sourced from `local.properties` (a local, untracked file — see `app/build.gradle.kts`):

```properties
# local.properties
API_BASE_URL=http://YOUR_SERVER_IP:8080/
```

If `API_BASE_URL` is absent from `local.properties`, it falls back to the same address as a
default. Change this line and rebuild to point the app at a different backend. Trailing slash
matters (Retrofit's `baseUrl` requires it).

If the target backend uses **HTTPS**, also update `app/src/main/res/xml/network_security_config.xml`
(see section 8, "Network Security").

## 4. Building a Release APK

```bash
./gradlew assembleRelease
```

Output: `app/build/outputs/apk/release/app-release.apk` (or `app-release-unsigned.apk` if no
signing config is configured — see below).

Release builds now have (as of Module 22):
- `isMinifyEnabled = true` / `isShrinkResources = true` (R8 code/resource shrinking)
- Verbose logging fully compiled out (`AppLogger` and `HttpLoggingInterceptor` are both gated on
  `BuildConfig.DEBUG`, which is `false` in release)
- `proguard-rules.pro` covers this app's Retrofit interfaces and `@Serializable` models; Retrofit,
  OkHttp, kotlinx.serialization, and Hilt each also ship their own consumer ProGuard rules bundled
  in their libraries, which R8 applies automatically

**Compile-time verified** via `./gradlew assembleRelease` during this module. **Not yet verified
by running the actual release build on a device** — before shipping, install a release APK on a
real device and smoke-test login → home → fill checksheet → submit → history → notifications, since
R8 shrinking/obfuscation issues (if any slipped through) only surface at runtime, not at compile
time.

## 5. Generating a Signed Release APK

No real signing keystore exists in this environment (and none should ever be committed to source —
see Security Review below). Release signing is **opt-in** via `local.properties`, so the build
never has to hardcode a keystore path or password.

**Step 1 — generate a keystore** (do this once, store the `.jks` file and passwords somewhere
safe, e.g. a password manager — losing it means you can never update the app under the same
signature again):

```bash
keytool -genkeypair -v \
  -keystore bl-dcms-release.jks \
  -alias bl-dcms \
  -keyalg RSA -keysize 2048 -validity 10000
```

**Step 2 — add these four properties to `local.properties`** (never commit this file):

```properties
RELEASE_STORE_FILE=/absolute/path/to/bl-dcms-release.jks
RELEASE_STORE_PASSWORD=your-store-password
RELEASE_KEY_ALIAS=bl-dcms
RELEASE_KEY_PASSWORD=your-key-password
```

**Step 3 — build:**

```bash
./gradlew assembleRelease
```

When all four properties are present, `app/build.gradle.kts` automatically attaches a `release`
signing config and the output APK is signed and ready to distribute. When any property is missing,
the build still succeeds exactly as before (unsigned release APK) — nothing breaks either way.

## 6. Installing via adb

```bash
# Debug build
adb install -r app/build/outputs/apk/debug/app-debug.apk

# Signed release build
adb install -r app/build/outputs/apk/release/app-release.apk
```

Use `adb install -r` (reinstall, keep data) rather than a fresh install when upgrading over an
existing install so the technician doesn't need to log in again unnecessarily. If installing a
release build over a debug build (or vice versa) with different signing keys, `adb` will reject it
with `INSTALL_FAILED_UPDATE_INCOMPATIBLE` — uninstall the previous build first in that case.

## 7. Required Backend Version

This build depends on backend endpoints/response fields added through Module 20:

- `GET /checksheet/` must accept `locomotive_type`, `technology`, `work_type`, and `sort_by` query
  parameters, and its response items must include `locomotive_number`, `locomotive_type`,
  `technology`, `equipment_name`, and `section_name` (added in Module 20 — Advanced Search &
  Filtering).
- The Notification Center API (`GET /notifications/`, `PATCH /notifications/{id}/read`,
  `PATCH /notifications/read-all`) added in Module 19 must be present.

Run the backend's own test suite (`venv/bin/python -m pytest tests/ -q`) and confirm the server is
started (e.g. `uvicorn main:app`) before testing the app end-to-end. This app does not perform any
version negotiation with the backend — an older backend missing these fields/endpoints will not
crash the app (all new fields are optional/nullable and degrade to blank/"-" display), but Search &
Filtering and Notifications will not function correctly.

## 8. Release Checklist

| Item | Status |
|---|---|
| Application icon | `res/drawable-nodpi/logo.png` (500×500 PNG), referenced as `@drawable/logo`. Functional at all densities. Consider migrating to an adaptive icon (`mipmap-anydpi-v26` + foreground/background layers) for a more polished launcher appearance — not done here, no source layers were available and this is a visual/asset change, not a hardening one. |
| Version Code / Version Name | `versionCode = 1`, `versionName = "1.0"` in `app/build.gradle.kts`. Bump both for every release you ship; `versionCode` must strictly increase for Play Store / MDM updates to be accepted. |
| Manifest permissions | Only `android.permission.INTERNET` — minimal, no unnecessary permissions. |
| Manifest — backup | `android:allowBackup="false"` (changed in Module 22 — previously `true`). Prevents the DataStore-held session token from being included in Android's auto backup/cloud backup or `adb backup`. Revert to `true` only if you have a specific reason to support device-to-device data transfer and are comfortable with the token being included. |
| Network Security | `android:networkSecurityConfig="@xml/network_security_config.xml"` (replaces the old blanket `usesCleartextTraffic="true"`, same effective behavior today - cleartext is still permitted, since the current backend is plain HTTP). **Before a production release**, move the backend behind HTTPS and tighten this file to a `domain-config` scoped to the production host with `cleartextTrafficPermitted="false"`, instead of the current `base-config` that permits cleartext everywhere. |
| Deep Links | None defined — the app only has one `MAIN`/`LAUNCHER` intent filter. Not applicable. |
| Signing | See section 5. No signing config present in this environment by default (opt-in via `local.properties`). |
| Debuggable | Not explicitly set in `buildTypes.release` - AGP defaults `release.debuggable` to `false`, and debug builds are `true` by default. No override needed or added. |

## 9. Production Hardening Summary (Module 22)

- **Centralized error mapping** (`util/ApiErrorMapper.kt`): a single table maps HTTP 400/401/403/
  404/409/422/429/500/502/503/504 to user-friendly messages, replacing several duplicated
  `when (e.code())` blocks (Login, OTP, and two identical `mapPdfHttpError` copies in
  `HistoryViewModel`/`ChecksheetDetailViewModel`). Call sites that need a status code to mean
  something different (e.g. Login/OTP's 401 = "wrong credentials", not "session expired") pass an
  `overrides` map, so no screen's visible error text changed except previously-unhandled codes,
  which now show a real message instead of a raw Retrofit exception string.
- **Centralized debug-only logging** (`util/AppLogger.kt`): every raw `android.util.Log` call in
  Login/OTP/Splash/`NetworkModule` now goes through `AppLogger`, which is a no-op unless
  `BuildConfig.DEBUG` is true. Release builds emit nothing from these call sites.
  `HttpLoggingInterceptor` was already correctly gated to `NONE` in release (unchanged). Audited
  every log call for password/OTP/JWT/Authorization-header values — none were ever logged.
- **Global session-expiry handling**: `AuthInterceptor` now also inspects the response and clears
  the stored session (`SessionRepository.clearSession()`) whenever an authenticated request (one
  that carried a token) gets back a 401 — meaning the token expired or was revoked server-side.
  Login/OTP requests never carry a token, so their own "wrong credentials" 401 is unaffected. A new
  `SessionWatcherViewModel` + a `LaunchedEffect` in `MainActivity`'s `ChecksheetNavHost` observe
  session validity and navigate back to Login automatically from any authenticated screen the
  moment the session becomes invalid, without interfering with Splash's own cold-start token check
  or Login/OTP's own error handling.
- **Double-tap guard**: `LoginViewModel.requestOtp()` was missing the
  `if (_uiState.value.isLoading) return` guard that every other network-triggering action in the
  app already has (the UI-level `enabled = !state.isLoading` on the button already prevented this
  in practice; the guard adds defense-in-depth consistent with the rest of the codebase).
- **Release build hardening**: fixed a misplaced `proguard-rules.pro` (was at
  `app/src/main/proguard-rules.pro`, where AGP's `proguardFiles("proguard-rules.pro")` reference
  could never find it — R8 was silently building without any project-specific rules). Moved it to
  `app/proguard-rules.pro`, added rules for this app's Retrofit interfaces and serializable models,
  and enabled `isMinifyEnabled`/`isShrinkResources` for `release`.
- **Manifest security**: `allowBackup` set to `false`; `usesCleartextTraffic` replaced with a
  structured, documented `network_security_config.xml`.
- **Security review**: confirmed no hardcoded secrets/credentials anywhere in source; confirmed the
  Authorization header is injected in exactly one place (`AuthInterceptor`); confirmed
  `API_BASE_URL` is `BuildConfig`-based, not hardcoded.
- **Dependency audit**: no unused or duplicate dependencies found.
  `com.google.android.material:material` looked like a candidate for removal (the app is 100%
  Compose) but is actually required — `res/values/themes.xml`'s `Theme.Checksheet` parents
  `Theme.MaterialComponents.DayNight.NoActionBar`, which comes from that library.
  `material-icons-extended` is used extensively across the UI. `./gradlew lint` flags 8 dependencies
  with newer versions available (`GradleDependency` warnings) — not bumped in this module, since
  major-version jumps (e.g. Compose BOM 2024.06 → 2026.06) carry real compatibility risk beyond
  what `assembleDebug`/`testDebugUnitTest`/`lint` alone can verify; recommend a dedicated
  dependency-upgrade pass with full regression testing.
- **Exception handling audit**: every repository call site that can throw is already wrapped by its
  calling ViewModel in `catch (HttpException) / catch (IOException) / catch (Exception)` — no
  crash-from-networking gaps found. Every write-action ViewModel method (submit, save, approve,
  reject, logout, mark-as-read, etc.) already guards against double-invocation via an
  `isLoading`/`isProcessing`-style flag, except the one Login gap fixed above.
- **Input validation audit**: OTP (digits only, max 6), Locomotive Number search (digits only, max
  5), and Approve/Reject (reject requires a non-blank reason) were all already validated. No new
  validation rules were invented for Employee ID format, since no documented format constraint
  exists to validate against beyond the existing non-empty check.

## 10. Known Residual Items (not fixed in this module — flagged for a future pass)

- `network_security_config.xml` still permits cleartext traffic globally, matching today's
  HTTP-only dev backend. Lint's `InsecureBaseConfiguration` warning on this file is expected and
  documented — tighten it when the backend moves to HTTPS.
- App icon is a single flat PNG in `drawable-nodpi/`, not an adaptive icon. Cosmetic only.
- 8 dependencies have newer versions available (see `./gradlew lint` `GradleDependency` warnings).
- Release APK has been compile-verified (`assembleRelease` succeeds) but not yet installed and
  smoke-tested on a physical device in this environment.
