# BL-DCMS User Manual

**Supervisor & Technician Guide**

Prepared for: **Electric Loco Shed, BL**
Version 1.0 · July 2026
Document Class: Operational Use — For Technician & Supervisor use; Administrator functions not covered

BL- Digital Checksheet Management System

Architecture Developed By: **Mr. Jatinkumar Pardeshi** & **Mr. Neelkumar Patel**
Approving Authorities: **Sr. DEE/TRS/BL — Mr. R. C. Meena** & **DEE/TRS/BL — Mr. Suresh Kumar**

---

## 2. Revision History

> **About the Name:** **BL-DCMS** stands for **BL- Digital Checksheet Management System**, where **BL** is the code for Electric Loco Shed, Valsad.

This manual is reviewed whenever the Android application or Dashboard changes in a way that affects daily Technician or Supervisor use. Always confirm you are reading the current version before relying on it for a procedure.

| Version | Date | Prepared By | Summary of Changes |
|---|---|---|---|
| 1.0 | 28-Jul-2026 | BL-DCMS Documentation Team | Initial release — Supervisor & Technician workflows, login & OTP, checksheet filling, review, digital signature, PDF, troubleshooting, and FAQ. |

> **Note:** Superseded copies should be discarded. Keep only the latest version in circulation at your shed's noticeboard or shared drive.

---

## 3. Table of Contents

**Getting Started**
- [4. Introduction](#4-introduction)
- [5. System Overview](#5-system-overview)
- [6. User Roles](#6-user-roles)
- [7. Technician Workflow](#7-technician-workflow)
- [8. Supervisor Workflow](#8-supervisor-workflow)

**Signing In**
- [9. Login Process](#9-login-process)
- [10. OTP Authentication](#10-otp-authentication)
- [11. Android Application Overview](#11-android-application-overview)
- [12. Dashboard Overview](#12-dashboard-overview)

**Filling a Checksheet**
- [13. Filling a Checksheet](#13-filling-a-checksheet)
- [14. Selecting Locomotive](#14-selecting-locomotive)
- [15. Selecting Equipment](#15-selecting-equipment)
- [16. Completing Checksheet](#16-completing-checksheet)
- [17. Saving Progress](#17-saving-progress)
- [18. Submitting Checksheet](#18-submitting-checksheet)

**Review & Approval**
- [19. Supervisor Review Process](#19-supervisor-review-process)
- [20. Digital Signature Process (emBridge)](#20-digital-signature-process-embridge)
- [21. PDF Generation](#21-pdf-generation)

**Records & Search**
- [22. Viewing Previous Checksheets](#22-viewing-previous-checksheets)
- [23. Search & Filters](#23-search--filters)

**Help & Reference**
- [24. Common Error Messages](#24-common-error-messages)
- [25. Troubleshooting](#25-troubleshooting)
- [26. Frequently Asked Questions](#26-frequently-asked-questions)
- [27. Best Practices](#27-best-practices)
- [28. Do's and Don'ts](#28-dos-and-donts)
- [29. Contact Information](#29-contact-information)
- [30. Appendix](#30-appendix)

---

## 4. Introduction

BL-DCMS (BL- Digital Checksheet Management System, where BL is the code for Electric Loco Shed, Valsad) is the digital replacement for the paper checksheets used during electric locomotive maintenance at Electric Loco Shed, BL. It lets a Technician fill an inspection checksheet on a phone or tablet, and a Supervisor review and formally approve it — with a real digital signature — on a computer, without either side handling a paper form.

This manual explains how to use BL-DCMS for your day-to-day work. It is written for two audiences only:

- **Technicians**, who fill and submit checksheets on the Android application.
- **Supervisors**, who review, approve, or reject submitted checksheets on the web Dashboard.

> **Note:** System configuration, user accounts, locomotive/equipment records, and checksheet templates are managed by your shed's Administrator and IT department. Those functions are intentionally not covered in this manual — it focuses only on the screens and actions you will use daily.

### How to Read This Manual

Each procedure is written as short, numbered steps. Along the way you will see four kinds of callouts:

> **Note:** Background information that helps the instruction make sense.

> **Tip:** A shortcut or good habit that makes the task easier.

> **Caution:** Something to double-check before you continue, to avoid a mistake.

> **Warning:** An action that cannot be undone, or a rule that must not be broken.

---

## 5. System Overview

BL-DCMS has two faces that work together on the same set of checksheet records, so everyone always sees the current, correct status:

**Android App**
- Used by Technicians in the shed, on a phone or tablet
- Log in, select a locomotive and equipment, fill and submit a checksheet
- Track the status of your own submissions
- View and download the signed PDF once approved

**Web Dashboard**
- Used by Supervisors from an office computer or laptop
- Review checksheets submitted by Technicians in your section
- Approve with a digital signature, or reject with a reason
- View, download, and search past checksheets

### The Checksheet Lifecycle

Every checksheet moves through the same five stages, in this order. You will see these exact status names throughout the app and Dashboard.

```
DRAFT  →  SUBMITTED  →  UNDER REVIEW  →  APPROVED  or  REJECTED
```

A Technician controls the checksheet up to Submitted. From Submitted onward, only a Supervisor can move it forward — a Technician cannot approve their own work.

---

## 6. User Roles

Your account is set up with exactly one role by your Administrator. What you see in the app or Dashboard depends entirely on that role.

| Role | Primary Responsibility | Where They Work |
|---|---|---|
| **Technician** | Fill and submit checksheets for locomotives/equipment assigned to their section; track their own submission history. | Android Application |
| **Supervisor** | Review checksheets submitted within their section; approve with a digital signature or reject with a reason. | Web Dashboard |

> **Note:** A third role, **Administrator**, exists to manage user accounts, locomotives, equipment, and checksheet templates for the whole shed. Administrator screens and functions are outside the scope of this manual. If you need a new account, a password reset, or a change to a checksheet template, contact your shed's IT coordinator (see Section 29, Contact Information) rather than looking for these options yourself.

---

## 7. Technician Workflow

This is the complete path a Technician follows for one checksheet, start to finish. Each step is explained in full later in this manual — use this page as your map.

```
Login → Verify OTP → Select Locomotive → Select Equipment → Fill Checksheet
    → Save as You Go → Submit → Track Status → View Signed PDF
```

### Section Map
- Sections 9–10: Logging in and verifying your OTP
- Section 11: A tour of the Android application
- Sections 13–18: Selecting a locomotive/equipment and filling out and submitting the checksheet
- Section 21: Viewing your PDF once a Supervisor approves
- Sections 22–23: Checking status and finding past checksheets

---

## 8. Supervisor Workflow

This is the complete path a Supervisor follows to clear one submitted checksheet.

```
Login → Open Checksheets List → Filter: Submitted → Open a Checksheet
    → Review Entries → Approve & Sign (or Reject) → Technician Notified
```

### Section Map
- Sections 9–10: Logging in and verifying your OTP
- Section 12: A tour of the Dashboard
- Section 19: Reviewing a submitted checksheet
- Section 20: Approving with a digital signature (emBridge)
- Sections 22–23: Checking status and finding past checksheets for your section

> **Tip:** Review submitted checksheets promptly. A Technician cannot start new work against the same equipment record until you approve or reject the one waiting in front of you.

---

## 9. Login Process

Both the Android application and the Dashboard use the same first step: your Employee ID and password. This applies whether you are a Technician or a Supervisor.

1. **Open the app or Dashboard.** Technicians: open the BL-DCMS app on your device. Supervisors: open the Dashboard address in your browser.
2. **Enter your Employee ID.**
3. **Enter your Password.** Use the eye icon to show/hide what you have typed and confirm it is correct.
4. **Tap or click Login.** You will be taken to the OTP screen next — see Section 10.

> **Note:** Your Employee ID and initial password are issued by your Administrator when your account is created.

> **Caution:** If you forget your password, do not keep guessing — repeated failed attempts can temporarily lock your account. Contact your IT coordinator (Section 29) for a reset.

---

## 10. OTP Authentication

After your Employee ID and password are accepted, BL-DCMS asks for a One-Time Password (OTP) as a second check. This confirms it is really you signing in, even if someone else knew your password.

1. **Wait for the OTP screen to appear** after a successful login.
2. **Enter the 6-digit code** into the OTP boxes.
3. **Submit / Verify.** You are signed in and taken to your Home screen (Technician) or Checksheets list (Supervisor).

> **Tip:** If the OTP does not arrive in time, wait for the on-screen countdown to finish and use **Resend** rather than re-entering an old code.

> **Warning:** Never share your OTP with anyone, including a colleague or someone claiming to be from IT. Nobody needs your OTP except you, at the moment you are logging in.

---

## 11. Android Application Overview

Once logged in, Technicians land on the Home screen — the starting point for every task.

### Main Areas

| Area | What It's For |
|---|---|
| **Fill Checksheet** | Start a new checksheet — select a locomotive and equipment, then fill it in. |
| **History** | See every checksheet you have submitted and its current status. |
| **Notifications** | Alerts when a Supervisor approves or rejects one of your checksheets. |
| **Profile** | Your account details, as set up by your Administrator. |

---

## 12. Dashboard Overview

Once logged in, Supervisors land on the Checksheets area of the Dashboard.

### Main Areas (Supervisor View)

| Area | What It's For |
|---|---|
| **Checksheets** | The list of checksheets submitted within your section — review, approve, or reject from here. |
| **Notifications** | Alerts when a new checksheet is submitted for your review. |

> **Note:** The Dashboard menu contains additional items (user management, reference data, system settings, and reports) that are only visible or usable by an Administrator. If a menu item does not open for you, that is expected — it is not part of the Supervisor role.

---

## 13. Filling a Checksheet

This section and the five that follow it (14–18) walk through one complete checksheet, in order. Follow them in sequence the first few times until the flow feels familiar.

```
14. Select Locomotive → 15. Select Equipment → 16. Complete Fields
    → 17. Save As You Go → 18. Submit
```

> **Tip:** Have the locomotive number and the physical equipment in front of you before you start. Filling a checksheet away from the equipment increases the risk of recording the wrong reading.

---

## 14. Selecting Locomotive

1. **Tap Fill Checksheet** on the Home screen.
2. **Enter the locomotive number** in the search box. Matching locomotives appear as you type.
3. **Select the correct locomotive** from the list.
4. **Confirm the details shown** (model and technology) match the locomotive physically in front of you before continuing.

> **Caution:** Always double-check the locomotive number before proceeding. A checksheet recorded against the wrong locomotive creates an incorrect maintenance record that is difficult to correct after submission.

---

## 15. Selecting Equipment

1. **Choose the equipment or assembly** being inspected from the list shown for the selected locomotive. Only equipment relevant to that locomotive's section is listed.
2. **Select the maintenance/work type** if prompted.
3. **Confirm** to load the correct checksheet template for that equipment.

> **Note:** The checksheet that opens is built specifically for the equipment you selected — the questions, fields, and acceptable ranges are pre-defined by your Administrator for that equipment type.

---

## 16. Completing Checksheet

A checksheet is made up of one or more pages of fields. The field types you will see are:

| Field Type | What You Do |
|---|---|
| **Text** | Type a short observation or remark. |
| **Number** | Enter a numeric reading. |
| **Numeric Range** | Enter a reading that is checked against a standard range. See the caution below. |
| **Dropdown / List** | Choose one option from a fixed list. |
| **Date / Time** | Pick a date or time using the on-screen picker. |
| **Grouped Fields** | A set of related readings shown together, e.g. three-phase readings (U / V / W) under one heading. |

> **Caution — Numeric Range Fields:** If a reading you enter falls outside the prescribed standard range, BL-DCMS does not silently accept or block it — it shows a confirmation dialog asking you to confirm the value is correct as read. Only confirm if you have re-checked the reading and it is genuinely correct; do not confirm out of habit.

### Moving Between Pages

Longer checksheets are split across multiple pages. Use **Next** and **Previous** to move between them; a progress indicator at the top shows which page you are on.

> **Tip:** Fields marked as mandatory must be completed on every page before you can submit. If Submit does not work, BL-DCMS will take you straight to the first incomplete field.

---

## 17. Saving Progress

A checksheet you have started but not yet submitted is a `DRAFT`. Your entries are kept as you move between pages, so you do not need to re-type earlier answers if you navigate back and forth.

1. **Continue filling fields as normal** — there is no separate "Save" button to press after every field.
2. **If you need to stop partway through**, leave the checksheet screen using the back navigation rather than force-closing the app.
3. **Return to Fill Checksheet later** to resume where you left off.

> **Caution:** A poor network connection can interrupt a checksheet still in progress. If you notice a page failed to load correctly, check your connection before continuing rather than proceeding on a guess.

---

## 18. Submitting Checksheet

1. **Reach the last page** of the checksheet and review your entries.
2. **Tap Submit.**
3. **Confirm in the dialog** that appears. This dialog exists because submitting is final — read the warning below.
4. **The checksheet status changes to** `SUBMITTED` **and is sent to your section's Supervisor** for review.

> **Warning:** Once submitted, a checksheet **cannot be edited** by the Technician. Review every entry carefully on the last page before tapping Submit. If a genuine mistake is found afterward, it can only be corrected through the Supervisor's Reject decision (Section 19), which returns it to you with a stated reason.

---

## 19. Supervisor Review Process

1. **Open Checksheets** on the Dashboard.
2. **Filter to Submitted** to see what is waiting for your attention.
3. **Open a checksheet** to view every field the Technician entered, page by page.
4. **Look for any reading the Technician confirmed as outside the standard range** — these are shown clearly and deserve a closer look.
5. **Decide:**
   - **Approve** — proceed to Section 20 to digitally sign it, or
   - **Reject** — enter a clear reason and confirm.

> **Note:** A rejection reason is mandatory and is shown to the Technician, along with the checksheet's full contents, so they know exactly what to correct on their next attempt.

---

## 20. Digital Signature Process (emBridge)

Approving a checksheet in BL-DCMS is not just a status change — it is a real digital signature, applied using your personal USB signing token, in the same way a physical signature and stamp would be used on a paper form.

### Before You Begin (One-Time Setup)

- Your USB DSC (Digital Signature Certificate) token is installed and recognized by your computer.
- The **emBridge** signing service is installed and running on your computer.
- This one-time setup is normally done by your IT department when your Supervisor account is issued. If it has not been done, contact IT before your first approval.

### Signing a Checksheet

1. **Connect your USB signing token** to your computer.
2. **Open the checksheet under review** and click **Approve & Sign**.
3. **Wait for the four status checks** to complete: emBridge Installed → Service Running → Token Connected → Certificate Loaded.
4. **Select your certificate** from the list shown.
5. **Enter your token PIN** when prompted.
6. **Wait for confirmation.** The checksheet moves to `APPROVED` and a signed PDF is generated automatically (Section 21).

> **Note:** If any status check fails partway through, the checksheet remains `UNDER REVIEW` — nothing is ever partially approved. See Section 25, Troubleshooting, for what each failure means.

> **Warning:** Never share your token PIN with anyone, and never leave your USB token unattended while inserted in a shared computer. Signing with your token and PIN is legally attributed to you personally.

---

## 21. PDF Generation

As soon as a Supervisor approves and digitally signs a checksheet, BL-DCMS automatically generates a PDF copy laid out like the original paper form, carrying the digital signature.

1. **Open the approved checksheet** — from History (Android) or the Checksheets list (Dashboard).
2. **Choose View PDF** to open it, or **Download PDF** to save a copy.

> **Note:** Only `APPROVED` checksheets have a signed PDF. A rejected checksheet does not generate one — there is nothing to view or download for it.

---

## 22. Viewing Previous Checksheets

Technicians use **History** in the app; Supervisors use the **Checksheets** list on the Dashboard, scoped to their section. Both show the same five statuses:

| Status | Meaning |
|---|---|
| `DRAFT` | Started but not yet submitted. Still editable by the Technician. |
| `SUBMITTED` | Sent for review. Waiting for a Supervisor to open it. |
| `UNDER REVIEW` | A Supervisor has opened it and is actively reviewing/signing. |
| `APPROVED` | Digitally signed. Final — a signed PDF is available. |
| `REJECTED` | Sent back with a reason. Final for this record — a new checksheet is filled to redo the work. |

---

## 23. Search & Filters

When your list of checksheets grows long, narrow it down instead of scrolling.

1. **Enter a locomotive number** in the search box to find every checksheet for that locomotive.
2. **Apply a status filter** (e.g. only `REJECTED`) to focus on what needs attention.
3. **Apply a date range** to look back at a specific period.
4. **Clear filters** to return to the full list.

> **Tip:** Combine a locomotive number with a status filter to quickly answer "has this locomotive's checksheet been approved yet?"

---

## 24. Common Error Messages

| Message | What It Means | What To Do |
|---|---|---|
| `Invalid Employee ID or Password` | The credentials entered do not match a known account. | Re-check for typos. If it persists, contact IT (Section 29). |
| `OTP Expired` | The code was not entered within its validity window. | Use Resend to request a fresh code. |
| `Please complete all mandatory fields` | Submit was attempted with required fields still empty. | You will be taken to the first incomplete field — fill it and try again. |
| `No internet connection` | Your device cannot reach BL-DCMS right now. | Check Wi-Fi/mobile data and retry. |
| `Session expired, please log in again` | You were logged out automatically after a period of inactivity, for security. | Log in again — any submitted checksheets are unaffected. |
| `PDF not yet available` | The checksheet has not been approved yet, so no signed PDF exists. | Wait for Supervisor approval; only then is the PDF generated. |
| `emBridge Not Installed / Service Not Running` | The signing service is not active on this computer. | See Section 25, Troubleshooting — Digital Signature Fails. |
| `Token Not Connected` | The USB DSC token is not detected. | Reconnect the token firmly in a working USB port and retry. |
| `Incorrect PIN` | The token PIN entered was wrong. | Re-enter carefully. Repeated failures can lock the token — contact IT if unsure. |

---

## 25. Troubleshooting

**I can't log in**
- *Cause:* Wrong Employee ID/password, or account not yet active.
- *Solution:* Re-check what you typed. If it still fails after a careful retry, contact your IT coordinator rather than trying repeatedly.

**My OTP never arrives**
- *Cause:* Delivery delay, or the mobile number on your account is outdated.
- *Solution:* Wait for the countdown and use Resend once. If it still does not arrive, confirm your registered mobile number with IT.

**The app feels slow or a screen won't load**
- *Cause:* Weak network signal in parts of the shed.
- *Solution:* Move to an area with better signal, or wait and retry. Your entries already typed on the current page are not lost by a brief connection drop.

**I can't find the locomotive I need**
- *Cause:* Typo in the locomotive number, or the record does not exist yet.
- *Solution:* Double-check the number stenciled on the locomotive. If it genuinely is not listed, contact your Administrator — new locomotive records are added centrally.

**My numeric entry keeps showing a confirmation dialog**
- *Cause:* The value you entered is outside the standard range for that field — this is expected behavior, not a fault.
- *Solution:* Re-measure to be sure, then confirm only if the reading is genuinely correct as entered.

**Digital signature fails or won't start**
- *Cause:* emBridge not running, USB token not connected, or no certificate on the token.
- *Solution:* Check the four status indicators shown in the signing dialog in order (Installed → Running → Connected → Certificate) and resolve the first one that fails. Reconnecting the USB token or restarting the emBridge application resolves most cases. If the problem continues, contact IT.

**The signed PDF won't open or download**
- *Cause:* Weak connection during download, or the checksheet is not yet approved.
- *Solution:* Confirm the status shows APPROVED, then retry on a stronger connection.

**A checksheet has stayed on SUBMITTED for a long time**
- *Cause:* The Supervisor has not yet reviewed it.
- *Solution:* Technicians: this is expected while awaiting review — no action needed on your side. If it seems unusually delayed, follow up with your Supervisor directly.

---

## 26. Frequently Asked Questions

**Q. Can I edit a checksheet after submitting it?**
No. Submission is final for the Technician. If a correction is genuinely needed, the Supervisor must Reject it with a reason, after which a new checksheet is filled.

**Q. What happens if I enter a reading outside the standard range?**
BL-DCMS shows a confirmation dialog rather than blocking you outright — real equipment sometimes genuinely reads outside standard. Confirm only after re-checking the reading is correct.

**Q. Can I fill a checksheet without an internet or network connection?**
No, an active connection is required — the checksheet is saved to the central system as you work, not stored only on your device.

**Q. How long does my login session stay active?**
Your session eventually expires automatically for security if left inactive. If this happens, simply log in again — nothing already submitted is affected.

**Q. Who do I contact if I forget my password?**
Your shed's IT coordinator (Section 29). Passwords cannot be reset from within the app or Dashboard.

**Q. Can a Technician see why their checksheet was rejected?**
Yes. The Supervisor's rejection reason is always shown to the Technician together with the checksheet.

**Q. Is the digital signature legally valid, or just a formality?**
It is a real, legally recognized digital signature applied with the Supervisor's personal DSC token — equivalent in standing to a handwritten signature and stamp, not a cosmetic status change.

**Q. Can I use the app on any Android phone?**
Use the device provided or approved by your shed for this purpose. Contact IT if you are unsure whether your device is supported.

---

## 27. Best Practices

### For Technicians
- Confirm the locomotive number and equipment before you begin filling a checksheet.
- Take readings directly from the equipment while filling the form — do not fill from memory.
- Re-check any reading before confirming it as an out-of-range value.
- Review every page carefully before tapping Submit — submission cannot be undone.
- Keep your device charged and updated so you are not interrupted mid-checksheet.
- Report app or device problems to IT promptly rather than working around them.

### For Supervisors
- Review submitted checksheets promptly — a backlog delays the Technician's next task.
- Read every field, not only the ones flagged as out-of-range.
- Write rejection reasons clearly and specifically enough for the Technician to act on them.
- Keep your USB signing token secure and never leave it unattended in a shared computer.
- Confirm emBridge and your token are working before your review session, not mid-approval.

---

## 28. Do's and Don'ts

| Do | Don't |
|---|---|
| Verify the locomotive number before starting | Don't share your password, OTP, or token PIN with anyone |
| Take readings from the equipment, not from memory | Don't submit a checksheet you have not reviewed |
| Re-check out-of-range readings before confirming them | Don't confirm an out-of-range reading without re-checking it |
| Review every page before submitting | Don't leave a USB signing token unattended in a shared PC |
| Log out on a shared computer when finished | Don't force-close the app while a page is loading |
| Keep your USB signing token with you at all times | Don't try repeated password guesses — request a reset instead |
| Report technical problems to IT promptly | Don't approve a checksheet you have not actually reviewed |
| Write clear, specific rejection reasons | Don't attempt to fill a checksheet away from the equipment |

---

## 29. Contact Information

For any issue this manual could not resolve — account access, app/Dashboard problems, digital signature/emBridge/USB token issues, record corrections, or an urgent device-down situation — contact either of the two shed contacts below. Both look after all categories of issue.

| Contact | Phone |
|---|---|
| Jatinkumar Pardeshi | +91 86554 92417 |
| Neelkumar Patel | +91 86554 92384 |

---

## 30. Appendix

### A. Glossary

- **BL-DCMS** — BL- Digital Checksheet Management System, where BL is the code for Electric Loco Shed, Valsad — the platform covered by this manual.
- **Checksheet** — The digital inspection/maintenance form filled by a Technician for a specific locomotive and equipment.
- **Template** — The pre-defined set of fields and pages that make up a checksheet for a given equipment type, set up centrally by the Administrator.
- **OTP** — One-Time Password — a temporary code used as a second login check.
- **DSC** — Digital Signature Certificate — the credential on your USB token used to digitally sign an approval.
- **emBridge** — The signing software that connects a Supervisor's USB DSC token to BL-DCMS during approval.
- **PDF** — The signed document generated automatically once a checksheet is approved.

### B. Status Legend

| Status | Meaning |
|---|---|
| `DRAFT` | Being filled, not yet submitted. |
| `SUBMITTED` | Sent to the Supervisor, awaiting review. |
| `UNDER REVIEW` | Supervisor is actively reviewing it. |
| `APPROVED` | Digitally signed — final, PDF available. |
| `REJECTED` | Returned with a reason — final for this record. |

### C. Quick Reference Card

**Technician**
1. Login → OTP → Home
2. Fill Checksheet → Locomotive → Equipment
3. Complete all pages → Submit
4. Track status in History
5. View PDF once Approved

**Supervisor**
1. Login → OTP → Checksheets
2. Filter: Submitted → Open
3. Review every field
4. Approve & Sign (USB token + PIN) or Reject with reason
5. Technician notified automatically

> **End of Manual.** Keep this manual accessible at your workstation. For anything not covered here, use the contacts in Section 29.
