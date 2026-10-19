#!/usr/bin/env python3
"""Bounded full-stack startup diagnostics; preserves containers' volumes and data.

Run from the repository root. Reports/logs go outside the checkout by default.
Stops the stack between cycles and leaves the final cycle running.
"""
import argparse
import datetime
import json
from pathlib import Path
import re
import subprocess
import time
import urllib.request


def command(*args):
    return subprocess.run(args, capture_output=True, text=True, timeout=300)


def get(url):
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            return response.read().decode(), response.status
    except Exception as error:
        raise RuntimeError(f'{url}: {error}') from error


def smoke(frontend, backend):
    catalog, _ = get(backend + '/api/projects?lang=en&page=1')
    projects = json.loads(catalog)['projects']
    if not projects:
        raise ValueError('Catalog has no projects: cannot validate a real project page')
    html, status = get(frontend + '/?lang=en')
    if 'class="project"' not in html or 'role="alert"' in html:
        raise ValueError('HTTP 200 without a functional catalog')
    slug = projects[0]['slug']
    project, project_status = get(frontend + '/projects/' + slug + '?lang=en')
    if 'reader' not in project or 'role="alert"' in project:
        raise ValueError('Project reader did not render')
    scripts = set(re.findall(r'<script[^>]+src="([^"]+)"', html + project))
    if not scripts:
        raise ValueError('No JavaScript assets in rendered pages')
    for script in scripts:
        asset, _ = get(frontend + script.replace('&amp;', '&'))
        if not asset or asset.lstrip().startswith('<!DOCTYPE'):
            raise ValueError('Invalid JavaScript response: ' + script)
    return {'home': status, 'project': project_status, 'slug': slug, 'javascript_assets': len(scripts)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cycles', type=int, default=5)
    parser.add_argument('--timeout', type=int, default=180)
    parser.add_argument('--frontend', default='http://127.0.0.1:3099')
    parser.add_argument('--backend', default='http://127.0.0.1:3098')
    parser.add_argument('--output', default='/tmp/engineering-library-startup-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    args = parser.parse_args()
    if args.cycles < 1 or args.timeout < 1:
        parser.error('cycles and timeout must be positive')
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    config = command('docker', 'compose', 'config', '--quiet')
    if config.returncode:
        raise RuntimeError(config.stderr)
    for name, arguments in (
        ('initial-state.log', ('ps', '--all', '--format', 'json')),
        ('initial-containers.log', ('logs', '--timestamps', '--tail=300')),
    ):
        initial = command('docker', 'compose', *arguments)
        (output / name).write_text(initial.stdout + initial.stderr)
        if initial.returncode:
            raise RuntimeError(initial.stderr)
    results = []
    for cycle in range(1, args.cycles + 1):
        stopped = command('docker', 'compose', 'stop')
        if stopped.returncode:
            raise RuntimeError(stopped.stderr)
        since = datetime.datetime.now(datetime.timezone.utc).isoformat()
        start = time.monotonic()
        up = command('docker', 'compose', 'up', '--build', '-d')
        (output / f'{cycle}-compose.log').write_text(up.stdout + up.stderr)
        result = {'cycle': cycle, 'since': since, 'compose_exit': up.returncode, 'observations': []}
        deadline = time.monotonic() + args.timeout
        if up.returncode == 0:
            while time.monotonic() < deadline:
                try:
                    checks = smoke(args.frontend, args.backend)
                    state = command('docker', 'compose', 'ps', '--all', '--format', 'json')
                    states = [json.loads(line) for line in state.stdout.splitlines() if line.strip()]
                    if len(states) != 3 or any(s.get('State') != 'running' or s.get('Health') != 'healthy' for s in states):
                        raise ValueError('Stack not yet fully healthy')
                    checks['postgres'] = command('docker', 'compose', 'exec', '-T', 'postgres', 'sh', '-c', 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"').returncode
                    if checks['postgres']:
                        raise ValueError('PostgreSQL not ready')
                    result.update(success=True, checks=checks, states=[
                        {key: state.get(key) for key in ('Service', 'State', 'Health', 'ExitCode', 'Status')}
                        for state in states
                    ])
                    break
                except Exception as error:
                    result['observations'].append({'seconds': round(time.monotonic() - start, 1), 'error': str(error)})
                    time.sleep(1)
        result.setdefault('success', False)
        result['seconds'] = round(time.monotonic() - start, 1)
        logs = command('docker', 'compose', 'logs', '--timestamps', '--since', since)
        (output / f'{cycle}-containers.log').write_text(logs.stdout + logs.stderr)
        frontend_logs = command('docker', 'compose', 'logs', '--timestamps', '--since', since, 'frontend')
        result['fatal_errors'] = [line for line in (frontend_logs.stdout + frontend_logs.stderr).splitlines()
                                  if re.search(r'Failed to compile|Module not found|Cannot find module|FATAL|uncaughtException|UnhandledPromiseRejection|EADDRINUSE|ENOENT', line)]
        if logs.returncode or frontend_logs.returncode or result['fatal_errors']:
            result['success'] = False
        results.append(result)
        (output / 'results.json').write_text(json.dumps(results, indent=2))
        print(json.dumps({key: value for key, value in result.items() if key not in ('observations', 'states')}), flush=True)
        if not result['success']:
            print('Failed cycle preserved for inspection; no automatic restart.', flush=True)
            break
    print('Evidence: ' + str(output), flush=True)
    return 0 if len(results) == args.cycles and all(r['success'] for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
