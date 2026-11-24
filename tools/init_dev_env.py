#!/usr/bin/env python3
"""Create local development credentials without replacing existing configuration."""
import os
from pathlib import Path
import secrets
import string


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


if __name__ == '__main__':
    main()
