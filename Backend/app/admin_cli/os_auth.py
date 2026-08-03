"""
Module 44: System Administration CLI - operating-system authentication and authorization.

The CLI intentionally implements NO login, password, or token of its own. Whoever can run this
process has already been authenticated by Linux itself (a local shell, or an SSH session -
sshd's own authentication, keys/passwords/PAM, already happened before this process ever
starts). This module's only job is *authorization*: confirming the already-authenticated OS user
is actually allowed to run privileged BL-DCMS admin commands, and - defense in depth, on top of
whatever firewall/sshd configuration already restricts access to the internal network - refusing
to run at all if it can tell (from SSH's own environment variables) that the connection
originated outside the organization's internal network.
"""
from __future__ import annotations

import grp
import ipaddress
import os
import pwd
import socket
from dataclasses import dataclass
from typing import Optional

# Module 44: only members of this Linux group may run privileged bldcms-admin commands. Created
# by scripts/install_admin_cli.sh; add trusted sysadmins to it with `usermod -aG bldcms-admin
# <user>`. Never bypassable from within this Python process - group membership is an OS-level
# fact this code can only read, not grant.
REQUIRED_GROUP = "bldcms-admin"

# Module 44: defense-in-depth network check, only evaluated when the CLI can tell (via SSH's own
# environment variables) that it's running inside an SSH session. A local console/tty login has
# no "source network" to check at all, so it is implicitly allowed - the primary control for
# "internal network only" is sshd/firewall configuration on the host, which is outside this
# codebase; this is a second, independent check on top of that, not a replacement for it.
# Override via the BLDCMS_ADMIN_ALLOWED_CIDRS environment variable (comma-separated) for
# environments whose internal range differs from the private-address defaults below.
DEFAULT_ALLOWED_CIDRS = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8"]


@dataclass(frozen=True)
class AuthorizationResult:
    allowed: bool
    linux_username: str
    source_host: Optional[str]
    reason: Optional[str] = None


def _current_linux_username() -> str:
    try:
        return pwd.getpwuid(os.getuid()).pw_name
    except Exception:
        # Extremely unlikely (would mean /etc/passwd has no entry for the running uid), but
        # audit logging must still have *something* to attribute the attempt to.
        return os.environ.get("USER") or os.environ.get("LOGNAME") or f"uid:{os.getuid()}"


def _current_user_group_names() -> set[str]:
    uid = os.getuid()
    try:
        primary_gid = pwd.getpwuid(uid).pw_gid
        group_ids = set(os.getgroups()) | {primary_gid}
    except Exception:
        group_ids = set(os.getgroups())

    names = set()
    for gid in group_ids:
        try:
            names.add(grp.getgrgid(gid).gr_name)
        except KeyError:
            continue
    return names


def _ssh_client_ip() -> Optional[str]:
    """Returns the connecting client's IP address if this process is running inside an SSH
    session, else None (meaning: not applicable, e.g. a direct console login)."""
    for var in ("SSH_CONNECTION", "SSH_CLIENT"):
        value = os.environ.get(var)
        if value:
            # SSH_CONNECTION="<client ip> <client port> <server ip> <server port>"
            parts = value.split()
            if parts:
                return parts[0]
    return None


def _allowed_cidrs() -> list[str]:
    override = os.environ.get("BLDCMS_ADMIN_ALLOWED_CIDRS")
    if override:
        return [cidr.strip() for cidr in override.split(",") if cidr.strip()]
    return DEFAULT_ALLOWED_CIDRS


def _is_within_internal_network(client_ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(client_ip)
    except ValueError:
        return False
    for cidr in _allowed_cidrs():
        try:
            if addr in ipaddress.ip_network(cidr, strict=False):
                return True
        except ValueError:
            continue
    return False


def _source_host() -> Optional[str]:
    client_ip = _ssh_client_ip()
    if client_ip:
        return client_ip
    try:
        return socket.gethostname()
    except Exception:
        return None


def authorize() -> AuthorizationResult:
    """The single entry point every bldcms-admin command must call before doing anything else.
    Never raises - returns a result the caller uses to either proceed or exit(1), so the caller
    can audit-log a denial (Result=Failure) before exiting, same as any other command outcome."""
    username = _current_linux_username()
    source_host = _source_host()

    client_ip = _ssh_client_ip()
    if client_ip and not _is_within_internal_network(client_ip):
        return AuthorizationResult(
            allowed=False,
            linux_username=username,
            source_host=source_host,
            reason=(
                f"Connection from {client_ip} is outside the configured internal network "
                f"ranges ({', '.join(_allowed_cidrs())}). This CLI is for internal "
                f"administration only."
            ),
        )

    group_names = _current_user_group_names()
    if REQUIRED_GROUP not in group_names and os.getuid() != 0:
        return AuthorizationResult(
            allowed=False,
            linux_username=username,
            source_host=source_host,
            reason=(
                f"Linux user '{username}' is not a member of the '{REQUIRED_GROUP}' group. "
                f"Ask a system administrator to run: usermod -aG {REQUIRED_GROUP} {username}"
            ),
        )

    return AuthorizationResult(allowed=True, linux_username=username, source_host=source_host)
