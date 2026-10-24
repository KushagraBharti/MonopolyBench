from __future__ import annotations

from collections import deque
import hashlib
import hmac
import os
import time
from urllib.parse import urlparse

from fastapi import Request, HTTPException
from starlette.responses import JSONResponse, RedirectResponse

COOKIE = "mb_session"
SESSION_SECONDS = 30 * 24 * 3600


class Auth:
    def __init__(self) -> None:
        self.password = os.environ.get("MB_DASHBOARD_PASSWORD", "")
        self.secret = os.environ.get("MB_SESSION_SECRET", "")
        self.token = os.environ.get("MB_EXPORT_TOKEN", "")
        if not self.password or len(self.secret) < 32 or not self.token:
            raise RuntimeError("Cloud mode requires MB_DASHBOARD_PASSWORD, MB_SESSION_SECRET (32+ characters), MB_EXPORT_TOKEN")
        self.attempts: deque[float] = deque()

    def sign(self, value: str) -> str:
        return hmac.new(self.secret.encode(), value.encode(), hashlib.sha256).hexdigest()

    def session(self) -> str:
        expires = str(int(time.time()) + SESSION_SECONDS)
        return expires + "." + self.sign(expires)

    def valid(self, cookie: str | None) -> bool:
        if not cookie:
            return False
        try:
            expires, signature = cookie.split(".")
            return int(expires) > time.time() and hmac.compare_digest(signature, self.sign(expires))
        except ValueError:
            return False

    def login(self, password: str) -> str:
        now = time.monotonic()
        while self.attempts and self.attempts[0] < now-60:
            self.attempts.popleft()
        if len(self.attempts) >= 10:
            raise HTTPException(429, "Too many login attempts; retry in one minute")
        self.attempts.append(now)
        if not hmac.compare_digest(password.encode(), self.password.encode()):
            raise HTTPException(401, "Incorrect password")
        return self.session()

    async def middleware(self, request: Request, call_next):
        path = request.url.path
        public = path in {"/api/health", "/api/auth/login", "/login"} or path.startswith("/assets/") or path == "/favicon.ico"
        export = request.method == "GET" and (path == "/api/exports" or path.startswith("/api/exports/") and path.endswith("/download") or path.startswith("/api/jobs/") and path.endswith("/export"))
        bearer = request.headers.get("authorization", "")
        token_ok = export and hmac.compare_digest(bearer, "Bearer " + self.token)
        if not public and not token_ok and not self.valid(request.cookies.get(COOKIE)):
            return JSONResponse({"detail": "Login required"}, status_code=401) if path.startswith("/api/") else RedirectResponse("/login", status_code=303)
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin = request.headers.get("origin")
            if origin and urlparse(origin).netloc != request.headers.get("host"):
                return JSONResponse({"detail": "Cross-origin mutation refused"}, status_code=403)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        return response
