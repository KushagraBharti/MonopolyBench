import http.cookiejar,json,subprocess,urllib.request
BASE='https://monopolybench-production.up.railway.app'
CLI='/tmp/mb-railway-cli/node_modules/.bin/railway'
result=subprocess.run([CLI,'variable','list','--service','17b95e30-fa26-4670-816e-0bd90f4f7bfd','--environment','a80674c4-1926-4519-9c84-3b33cfc1385e','--json'],capture_output=True,text=True,timeout=60)
if result.returncode:raise RuntimeError('Read-only Railway variable lookup failed')
variables=json.loads(result.stdout)
http=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def request(path,body=None):
    req=urllib.request.Request(BASE+'/api/'+path,data=None if body is None else json.dumps(body).encode(),headers={} if body is None else {'Content-Type':'application/json'})
    with http.open(req,timeout=180) as response:return json.load(response)
request('auth/login',{'password':variables['MB_DASHBOARD_PASSWORD']})
