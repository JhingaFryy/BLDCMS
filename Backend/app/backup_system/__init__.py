"""Module 44: Automated Backup System.

Writes scheduled, retention-managed backups (Daily/Weekly/Monthly) to a separate mounted HDD -
never to the SSD the application itself runs from. Entirely standalone: not imported by main.py
or any app/api/* router, and never reachable over HTTP - the only way to run anything in this
package is `python -m app.backup_system.run <daily|weekly|monthly|verify>`, normally invoked by
cron (see scripts/install_backup_cron.sh). This mirrors app/admin_cli's existing
"standalone-package-inside-app/, never HTTP-reachable" pattern.

This package only ever reads application data (database, PDFs, logs, source trees) to copy it
elsewhere - it never writes to or modifies anything the running application depends on.
"""
