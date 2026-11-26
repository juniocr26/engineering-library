import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from host_filesystem import json_write, mkdir, ws


def runtime_paths(root):
    exchange = mkdir(root / 'backend/storage/makedocs/filesystem/host')
    return exchange, exchange / 'lifecycle.json'


def read_status(path):
    try:
        with ws.directory(path.parent) as fd:
            return json.loads(ws.read(fd, path.name, 16384)[0])
    except FileNotFoundError:
        return {}


def ensure(root):
    exchange, status_path = runtime_paths(root)
    current = read_status(status_path)
    if current.get('uid') == os.getuid() and time.time() - current.get('at', 0) < 12:
        return current
    with ws.directory(exchange) as fd:
        log_fd = os.open('lifecycle.log', os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600, dir_fd=fd)
    with os.fdopen(log_fd, 'ab') as log:
        child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--supervise', str(root)],
                                 stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True,
                                 env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        current = read_status(status_path)
        if current.get('uid') == os.getuid() and time.time() - current.get('at', 0) < 12:
            return current
        if child.poll() not in (None, 0):
            raise RuntimeError('Host adapter lifecycle failed; inspect ' + str(exchange / 'lifecycle.log'))
        time.sleep(.1)
    raise RuntimeError('Host adapter lifecycle readiness timed out')


def stop(root):
    exchange, path = runtime_paths(root)
    state = read_status(path)
    pid = state.get('pid')
    if not pid or state.get('uid') != os.getuid():
        return
    try:
        command = subprocess.check_output(['ps', '-p', str(pid), '-o', 'args='], text=True)
    except subprocess.CalledProcessError:
        return
    if str(Path(__file__).resolve()) not in command or '--supervise ' + str(root) not in command:
        raise RuntimeError('Lifecycle process identity changed; refusing to signal it')
    os.kill(pid, signal.SIGTERM)
    deadline = time.monotonic() + 40
    while time.monotonic() < deadline:
        if read_status(path).get('pid') != pid:
            return
        time.sleep(.1)
    raise RuntimeError('Host adapter shutdown timed out; retained its state')


def supervise(root):
    if os.geteuid() == 0:
        raise RuntimeError('Run the host adapter as a normal user, never as root')
    exchange, path = runtime_paths(root)
    # The lifetime lock, rather than a PID file, prevents duplicate supervisors.
    with ws.directory(exchange) as directory:
        fd = os.open('lifecycle.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600, dir_fd=directory)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        return
    stopping = False
    def shutdown(*_):
        nonlocal stopping
        stopping = True
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    child = None
    def stop_child():
        nonlocal child
        if child and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=30)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=5)
        child = None
        # No other worker can own this exchange while our managed child is alive.
        ready = exchange / 'ready.json'
        if ready.exists():
            ready.unlink()
    try:
        json_write(exchange / 'managed.json', {'schema': 1, 'uid': os.getuid()})
        while not stopping:
            json_write(path, {'pid': os.getpid(), 'uid': os.getuid(), 'at': time.time(),
                              'workerPid': child.pid if child and child.poll() is None else None})
            running = False
            try:
                result = subprocess.run(['docker', 'compose', 'ps', '-q', 'backend'], cwd=root,
                                        capture_output=True, text=True, timeout=6)
                identifier = result.stdout.strip()
                if result.returncode == 0 and identifier and all(c in '0123456789abcdef' for c in identifier):
                    result = subprocess.run(['docker', 'inspect', '--format', '{{.State.Running}}', identifier],
                                            capture_output=True, text=True, timeout=6)
                    running = result.returncode == 0 and result.stdout.strip() == 'true'
            except (OSError, subprocess.TimeoutExpired):
                pass
            if running and (child is None or child.poll() is not None):
                child = subprocess.Popen([sys.executable, str(root / 'tools/host_filesystem.py'),
                                          '--library', str(root), '--exchange', str(exchange)],
                                         stdin=subprocess.DEVNULL,
                                         env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
            elif not running and child is not None:
                stop_child()
            for _ in range(20):
                if stopping:
                    break
                time.sleep(.1)
    finally:
        stop_child()
        path.unlink(missing_ok=True)
        os.close(fd)


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] != '--supervise':
        raise SystemExit('Use tools/init_dev_env.py for application startup and shutdown')
    supervise(Path(sys.argv[2]).absolute())
