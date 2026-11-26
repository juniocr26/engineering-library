#!/usr/bin/env python3
"""Initialize development and manage the user-scoped host adapter lifecycle."""
import os
from pathlib import Path
import secrets
import string
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parent.parent
    alphabet = string.ascii_letters + string.digits
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(12))
        if all(any(c in group for c in password) for group in
               (string.ascii_uppercase, string.ascii_lowercase, string.digits)):
            break
    content = (root / '.env.example').read_text().replace(
        'replace_with_generated_password', password).replace(
        'replace_with_generated_rails_secret', secrets.token_hex(64))
    if hasattr(os, 'getuid') and os.uname().sysname == 'Linux':
        content = content.replace('LOCAL_UID=1000', f'LOCAL_UID={os.getuid()}').replace(
            'LOCAL_GID=1000', f'LOCAL_GID={os.getgid()}')
    try:
        fd = os.open(root / '.env', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        print('Existing .env preserved.')
    else:
        with os.fdopen(fd, 'w') as target:
            target.write(content)
        print('Created local .env; credentials were not printed.')
    for folder in ('.dockerized-postgres',):
        (root / folder).mkdir(parents=True, exist_ok=True)
    if os.name != 'posix':
        raise SystemExit('The host filesystem adapter requires a POSIX environment; use WSL2 on Windows')
    from library_runtime import ensure, stop
    action = sys.argv[1] if len(sys.argv) > 1 else None
    if action not in (None, 'up', 'stop', 'down', 'restart', 'status'):
        raise SystemExit('Usage: python3 tools/init_dev_env.py [up|stop|down|restart|status] [Compose arguments]')
    if action in (None, 'up', 'restart'):
        state = ensure(root)
        print('Host filesystem lifecycle ready (PID ' + str(state['pid']) + ').')
    if action in ('up', 'stop', 'down', 'restart'):
        if action == 'down' and any(arg in ('-v', '--volumes', '--rmi') for arg in sys.argv[2:]):
            raise SystemExit('Destructive cleanup is not part of the application lifecycle')
        result = subprocess.run(['docker', 'compose', action, *sys.argv[2:]], cwd=root)
        if result.returncode:
            raise SystemExit(result.returncode)
        if action in ('stop', 'down'):
            # A partial frontend stop must not disable an otherwise running backend.
            running = subprocess.run(['docker', 'compose', 'ps', '-q', 'backend'], cwd=root,
                                     capture_output=True, text=True, timeout=10)
            if not running.stdout.strip():
                stop(root)
    elif action == 'status':
        from library_runtime import read_status, runtime_paths
        print(read_status(runtime_paths(root)[1]))


if __name__ == '__main__':
    main()
