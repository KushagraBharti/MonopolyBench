"""Start the local API and site, keeping them alive after a terminal/agent exits."""
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / 'output/local-site'


def listening(port: int) -> bool:
    with socket.socket() as connection:
        connection.settimeout(.5)
        return connection.connect_ex(('127.0.0.1', port)) == 0


def launch(name: str, command: list[str], cwd: Path, port: int) -> dict:
    url = f'http://127.0.0.1:{port}'
    if listening(port):
        return {'name': name, 'url': url, 'status': 'already listening; existing process preserved'}
    kwargs = {}
    if os.name == 'nt':
        kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_BREAKAWAY_FROM_JOB
    else:
        kwargs['start_new_session'] = True
    with (LOGS / f'{name}.log').open('ab') as stdout, (LOGS / f'{name}-error.log').open('ab') as stderr:
        process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, **kwargs)
    for _ in range(100):
        if listening(port):
            return {'name': name, 'url': url, 'pid': process.pid, 'status': 'started'}
        if process.poll() is not None:
            raise RuntimeError(f'{name} exited. See {LOGS / (name + "-error.log")}')
        time.sleep(.2)
    raise RuntimeError(f'{name} did not become ready. See {LOGS}')


def main() -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    python = ROOT / ('python/.venv/Scripts/python.exe' if os.name == 'nt' else 'python/.venv/bin/python')
    node = shutil.which('node')
    if not python.is_file() or not node:
        raise SystemExit('Install the Python workspace dependencies and Node.js first.')
    services = [launch('api', [str(python), '-m', 'uvicorn', 'monopoly_api.main:app', '--host', '127.0.0.1', '--port', '8000'], ROOT / 'python/apps/api', 8000),
                launch('site', [node, 'node_modules/vite/bin/vite.js', '--config', 'vite.config.mjs', '--host', '127.0.0.1', '--port', '5173', '--strictPort'], ROOT / 'frontend', 5173)]
    for service in services:
        check = service['url'] + ('/health' if service['name'] == 'api' else '/')
        with urllib.request.urlopen(check, timeout=5) as response:
            if response.status != 200:
                raise RuntimeError(f'{check} did not respond successfully')
    (LOGS / 'services.json').write_text(json.dumps(services, indent=2))
    print(json.dumps(services, indent=2))


if __name__ == '__main__':
    main()
