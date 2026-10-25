#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${MB_DEPLOY_URL:?Set MB_DEPLOY_URL to the Railway service HTTPS URL}"
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Refusing deployment: commit and review the working tree first." >&2
  exit 1
fi
if [[ "${1:-}" != "--force-interrupt" ]]; then
  : "${MB_DEPLOY_URL:?Set MB_DEPLOY_URL to the current deployment URL}"
  : "${MB_DASHBOARD_PASSWORD:?Set the dashboard password to check active jobs}"
  python - <<'PY'
import http.cookiejar, json, os, urllib.request
jar = http.cookiejar.CookieJar()
http = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
url = os.environ['MB_DEPLOY_URL'].rstrip('/')
if not url.startswith('https://'):
    raise SystemExit('Deployment status must use HTTPS')
data = json.dumps({'password': os.environ['MB_DASHBOARD_PASSWORD']}).encode()
http.open(urllib.request.Request(url+'/api/auth/login', data=data, headers={'Content-Type':'application/json'}), timeout=60).close()
status = json.load(http.open(url+'/api/status', timeout=60))
if status['active_workers']:
    raise SystemExit('Active games: pause the campaign and let them finish, or use --force-interrupt')
PY
fi
python scripts/build_manifest.py --git-sha "$(git rev-parse HEAD)"
bash scripts/verify.sh
railway variable set "MB_GIT_SHA=$(git rev-parse HEAD)" --skip-deploys
railway up
python - <<'PY'
import json, pathlib, datetime, os, time, urllib.request
deadline = time.monotonic() + 120
url = os.environ['MB_DEPLOY_URL'].rstrip('/') + '/api/health'
expected_sha = json.loads(pathlib.Path('build_info.json').read_text())['git_sha']
while True:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            health = json.load(response)
            if health.get('ok') and health.get('git_sha') == expected_sha:
                break
    except Exception:
        pass
    if time.monotonic() >= deadline:
        raise SystemExit('Deployment health check did not pass within 120 seconds')
    time.sleep(2)
with open('deploy_log.jsonl','a') as out:
    out.write(json.dumps({'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'build': json.loads(pathlib.Path('build_info.json').read_text())})+'\n')
PY
