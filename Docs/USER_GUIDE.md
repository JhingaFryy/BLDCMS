# User Guide

BL-DCMS has three roles — **Administrator**, **Supervisor**, and **Technician** — each with a
distinct workflow. Every permission described below is enforced by the backend on every
request, not just hidden in the UI.

---

## 1. Administrator Workflow (Dashboard)

Administrators manage the reference data and user accounts everything else depends on, and have
every permission a Supervisor has.

1. **Log in** to the Dashboard with an Employee ID and password.
2. **Manage users** — create Admin/Supervisor/Technician accounts (Users page), assign each
   Supervisor/Technician to a Section, deactivate accounts that should no longer log in.
3. **Manage reference data**:
   - **Sections** — the organizational units checksheets and users belong to.
   - **Locomotives** — loco number, model, and technology (e.g. WAP-5, WAG-9HC).
   - **Equipment** — the physical assemblies/sub-systems checksheets are filled against.
   - **Section–Equipment mapping** — which equipment types apply to which sections.
   - **Checksheet Templates & Template Fields** — the dynamic form definitions Technicians fill
     out (pages, groups, field types, validation ranges). New checksheet types are added here,
     not in application code.
4. **System Settings** — application-wide configuration exposed through the Dashboard.
5. **System Health** — the same live backend/database/notification-service status available via
   the `bldcms-admin health` CLI command, surfaced as a Dashboard page.
6. **Activity Logs & OTP Logs** — full audit visibility into authentication and checksheet
   lifecycle events.
7. Everything described under **Supervisor Workflow** below is also available to Admins.

## 2. Supervisor Workflow (Dashboard)

Supervisors review checksheets submitted by Technicians in their assigned Section(s).

1. **Log in** to the Dashboard.
2. **Checksheets page** — filter by status, locomotive, section, equipment, work type, and date
   range. A checksheet moves through:

   ```
   DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED
                                    └→ REJECTED
   ```

3. **Review a submitted checksheet** — open it to see every field the Technician entered, any
   out-of-range readings the Technician explicitly confirmed, and the full field-level layout
   matching the original paper form.
4. **Approve** — requires digitally signing with a connected USB DSC token via eMudhra
   emBridge (see §4 below). A checksheet cannot be approved without a successful signature.
5. **Reject** — requires a non-blank rejection reason, visible to the Technician on both the
   Dashboard and the Android app so they know what to correct.
6. **Notifications** — Supervisors are notified when a Technician in their section submits a
   checksheet; Technicians are notified when their checksheet is approved or rejected.

## 3. Technician Workflow (Android)

1. **Log in** — enter Employee ID and password.
2. **OTP verification** — a one-time password is required to complete login (delivered per your
   site's OTP configuration); enter it to receive a session token.
3. **Home** — see your assigned checksheets and recent activity.
4. **Fill a checksheet** — select a locomotive and equipment, then fill the dynamic,
   possibly-multi-page form. Field types include text, numbers, numeric ranges (with a
   confirmation dialog if your reading falls outside the prescribed standard), dropdowns,
   dates, times, and grouped/nested fields (e.g. per-phase readings U/V/W).
5. **Submit** — moves the checksheet from `DRAFT` to `SUBMITTED`, making it visible to your
   Section's Supervisor for review. A submitted checksheet can no longer be edited.
6. **History** — view every checksheet you've submitted and its current status (Submitted,
   Under Review, Approved, Rejected), including the rejection reason if applicable.
7. **Checksheet detail / PDF** — once a checksheet is approved, view or download its signed PDF
   directly from the app.
8. **Notifications** — receive a notification when a Supervisor approves or rejects your
   checksheet.

## 4. Digital Signature Workflow (eMudhra emBridge)

Approval is a real digital signature, not a database flag — Supervisors sign with a physical
USB DSC (Digital Signature Certificate) token through eMudhra's **emBridge** local service
running on their own Windows workstation. Full protocol and troubleshooting detail lives in
`Backend/docs/EMBRIDGE_INTEGRATION.md`; the day-to-day flow is:

### One-time setup per Supervisor PC

1. Ensure the CryptoID middleware and the USB DSC token (e.g. ProxKey) are installed and
   recognized by Windows.
2. Install emBridge from eMudhra's official site and confirm it's running (system tray icon
   reports "running").
3. In the browser used for BL-DCMS, visit `https://localhost.emudhra.com:26769` once and accept
   the one-time certificate warning (**Advanced → Proceed**, or your browser's equivalent).
   Skipping this step causes every signing attempt to fail even though emBridge is running.
4. If your network uses a corporate proxy, ask IT to exempt `localhost.emudhra.com` from it.

### Signing a checksheet

1. Connect the USB DSC token.
2. Open the checksheet under review in the Dashboard and click **Approve & Sign (emBridge)**.
3. The dialog checks, in order: emBridge installed → service running → USB token connected →
   certificate loaded — and tells you exactly which check failed if signing can't proceed.
4. Select the certificate on the token and enter its PIN when prompted.
5. On success, the checksheet moves to `APPROVED` and a signed PDF is generated. On any
   failure (wrong PIN, expired/mismatched certificate, cancelled signing), the checksheet stays
   in `UNDER_REVIEW` — nothing is ever partially approved.

The backend independently re-verifies the signature cryptographically and cross-checks the
certificate actually embedded in the signed PDF against the one declared at the start of
signing, as defense-in-depth against a compromised or misbehaving client.

## 5. PDF Generation

- A PDF is generated automatically once a checksheet reaches `APPROVED` status, laid out to
  match the original paper checksheet form for that equipment type.
- Supervisors and Technicians can view or download the PDF from the Dashboard's Checksheets
  page or the Android app's checksheet detail screen, respectively.
- Signed PDFs are stored under `Backend/storage/pdfs/` on the server and can be bulk-archived
  via the System Administration CLI (`bldcms-admin pdfs archive`) — see
  `Documentation/BACKUP_AND_RESTORE.md`.

## 6. Checksheet Workflow Summary

| Status | Set by | Meaning |
|---|---|---|
| `DRAFT` | Technician (auto-created) | Being filled, not yet visible to the Supervisor |
| `SUBMITTED` | Technician | Submitted, awaiting Supervisor pickup |
| `UNDER_REVIEW` | Supervisor (on opening it) | Actively being reviewed |
| `APPROVED` | Supervisor, via digital signature | Final — signed PDF generated |
| `REJECTED` | Supervisor, with a reason | Final — Technician notified with the reason |
