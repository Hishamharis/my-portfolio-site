"""
Usage:
    python manage.py log_update

What it does:
    - Reads your latest git commit (hash, message, author, changed files)
    - Grabs this machine's local IP address
    - Saves one row into the SiteUpdate table
    - Skips if that exact git hash is already logged (no duplicates)

If you are NOT using git, it will prompt you to type a version + summary manually.
"""

import subprocess
import socket
from django.core.management.base import BaseCommand
from portfolio.models import SiteUpdate


def _run(cmd):
    """Run a shell command and return stdout stripped, or empty string on failure."""
    try:
        return subprocess.check_output(
            cmd, shell=True, stderr=subprocess.DEVNULL
        ).decode().strip()
    except subprocess.CalledProcessError:
        return ''


def _get_local_ip():
    """Best-effort: get this machine's local network IP."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


class Command(BaseCommand):
    help = 'Log the latest git commit as a site update in the admin panel'

    def handle(self, *args, **options):
        # --- try to read git ---
        version       = _run('git rev-parse --short HEAD')
        summary       = _run('git log -1 --format=%s')          # subject line
        author        = _run('git log -1 --format="%an <%ae>"') # name <email>
        changed_files = _run('git diff-tree --no-commit-id -r --name-only HEAD')
        machine_ip    = _get_local_ip()

        # --- no git? fall back to manual input ---
        if not version:
            self.stdout.write(self.style.WARNING(
                'No git repo detected. Falling back to manual entry.\n'
            ))
            version = input('Version (e.g. v1.2 or 1.0): ').strip() or 'unknown'
            summary = input('Summary (what changed?): ').strip() or '—'
            author  = input('Author (optional): ').strip()
            changed_files = input('Changed files (comma-separated, optional): ').strip()

        # --- skip duplicate ---
        if SiteUpdate.objects.filter(version=version).exists():
            self.stdout.write(self.style.WARNING(
                f'Version "{version}" is already logged. Skipping.\n'
                f'Make a new commit first, then run this again.'
            ))
            return

        # --- save ---
        SiteUpdate.objects.create(
            version=version,
            summary=summary,
            changed_files=changed_files,
            author=author,
            machine_ip=machine_ip,
        )

        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Logged update\n'
            f'  Version : {version}\n'
            f'  Summary : {summary}\n'
            f'  Author  : {author or "—"}\n'
            f'  Files   : {changed_files or "—"}\n'
            f'  Machine : {machine_ip}\n'
        ))