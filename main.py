"""Manage the repository blocklist in the Windows hosts file."""

from __future__ import annotations

import argparse
import ctypes
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


SOURCE = Path(__file__).with_name("hosts.txt")
SYSTEM_HOSTS = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "drivers" / "etc" / "hosts"
START = b"# BEGIN ASIL-BACKDOOR-BLOCKLIST"
END = b"# END ASIL-BACKDOOR-BLOCKLIST"
LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z")


def load_domains(path: Path = SOURCE) -> list[str]:
    domains = set()
    for number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split()
        if len(fields) != 2 or fields[0] != "127.0.0.1":
            raise ValueError(f"{path}:{number}: expected '127.0.0.1 domain'")
        domain = fields[1].lower()
        labels = domain.split(".")
        if len(domain) > 253 or len(labels) < 2 or not all(LABEL.fullmatch(label) for label in labels):
            raise ValueError(f"{path}:{number}: invalid domain: {domain}")
        domains.add(domain)
    if not domains:
        raise ValueError(f"{path}: blocklist is empty")
    return sorted(domains)


def managed_lines(data: bytes) -> tuple[list[bytes], tuple[int, int] | None]:
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        raise ValueError("UTF-16 hosts files are not supported")
    lines = data.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if line.rstrip(b"\r\n") == START]
    ends = [i for i, line in enumerate(lines) if line.rstrip(b"\r\n") == END]
    if not starts and not ends:
        return lines, None
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        raise ValueError("hosts file has incomplete or duplicate blocklist markers")
    return lines, (starts[0], ends[0])


def render_block(domains: list[str], newline: bytes) -> bytes:
    entries = [START, *(f"127.0.0.1 {domain}".encode("ascii") for domain in domains), END]
    return newline.join(entries) + newline


def install_content(data: bytes, domains: list[str]) -> bytes:
    lines, bounds = managed_lines(data)
    newline = b"\r\n" if b"\r\n" in data or not data else b"\n"
    block = render_block(domains, newline)
    if bounds is None:
        separator = newline if data and not data.endswith((b"\r", b"\n")) else b""
        return data + separator + block
    start, end = bounds
    return b"".join(lines[:start]) + block + b"".join(lines[end + 1 :])


def remove_content(data: bytes) -> bytes:
    lines, bounds = managed_lines(data)
    if bounds is None:
        return data
    start, end = bounds
    return b"".join(lines[:start] + lines[end + 1 :])


def is_admin() -> bool:
    return bool(ctypes.windll.shell32.IsUserAnAdmin())


def request_elevation() -> None:
    args = subprocess.list2cmdline([str(Path(__file__).resolve()), *sys.argv[1:]])
    result = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, args, str(Path.cwd()), 1
    )
    if result <= 32:
        raise OSError(f"Administrator permission was not granted (ShellExecuteW: {result})")


def write_hosts(target: Path, content: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix="hosts-", dir=target.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        replace = ctypes.WinDLL("kernel32", use_last_error=True).ReplaceFileW
        replace.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_wchar_p,
                            ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
        replace.restype = ctypes.c_int
        if not replace(str(target), str(temporary), None, 0, None, None):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage the Asil Backdoor Blocklist in Windows hosts")
    parser.add_argument("command", nargs="?", default="install", choices=("install", "status", "remove"))
    args = parser.parse_args()

    try:
        if os.name != "nt":
            raise OSError("This installer supports Windows only")
        current = SYSTEM_HOSTS.read_bytes()
        domains = load_domains() if args.command != "remove" else []
        _, bounds = managed_lines(current)
        if args.command == "status":
            state = "not installed" if bounds is None else (
                "up to date" if install_content(current, domains) == current else "out of date"
            )
            print(f"Blocklist: {state} ({len(domains)} domains in source)")
            return 0

        updated = install_content(current, domains) if args.command == "install" else remove_content(current)
        if updated == current:
            print("No change needed.")
            return 0
        if not is_admin():
            request_elevation()
            print("Windows administrator permission requested; the elevated process will complete the change.")
            return 0

        write_hosts(SYSTEM_HOSTS, updated)
        print(f"Blocklist {args.command} complete.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
