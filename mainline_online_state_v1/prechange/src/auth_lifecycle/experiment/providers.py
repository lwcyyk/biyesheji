"""Adapters to two unmodified, complete native identity servers on loopback."""
import base64
from copy import deepcopy
import http.cookiejar
import json
from pathlib import Path
import secrets
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
PRIVATE = ROOT / ".runtime/l1"


class NativeError(RuntimeError):
    pass


class HTTP:
    def __init__(self, cookies=False):
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*args,**kwargs):return None
        handlers = [urllib.request.ProxyHandler({}),NoRedirect()]
        if cookies:handlers.append(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.opener = urllib.request.build_opener(*handlers)
        self.count=0

    def call(self, method, url, *, form=None, payload=None, headers=None, timeout=15):
        parsed = urllib.parse.urlsplit(url)
        if parsed.hostname != "127.0.0.1" or parsed.port not in {18080, 18081, 18082}:raise NativeError("non-study target rejected")
        h = dict(headers or {}); data = None
        if form is not None:data = urllib.parse.urlencode(form).encode(); h["Content-Type"] = "application/x-www-form-urlencoded"
        if payload is not None:data = json.dumps(payload).encode(); h["Content-Type"] = "application/json"
        request = urllib.request.Request(url, data=data, headers=h, method=method)
        self.count+=1
        try:
            response = self.opener.open(request, timeout=timeout)
        except urllib.error.HTTPError as error:response = error
        raw = response.read()
        try:body = json.loads(raw) if raw else {}
        except (ValueError, UnicodeDecodeError):body = {"non_json_response": True}
        return {"http": response.status, "body": body}


def required(response, *statuses):
    if response["http"] not in (statuses or (200,)):raise NativeError(f"native HTTP {response['http']}: {response['body'].get('error', 'request failed')}")
    return response["body"]


def claims(token):
    # Only decoding for identifying native fields. Signature verification is
    # performed by the independent witness, never inferred from this function.
    try:
        value = token.split(".")[1]; return json.loads(base64.urlsafe_b64decode(value + "=" * (-len(value) % 4)))
    except (ValueError, IndexError):return {}


class Keycloak:
    name = "keycloak"; version = "26.8.1"; base = "http://127.0.0.1:18080"; realm = "l1-research"
    native_record_kind = "user_session"
    root_action_kind = "terminate_owned_user_sessions"
    def __init__(self):
        self.http = HTTP(); self.admin_http = HTTP(); self.credentials = json.loads((PRIVATE/"secrets.json").read_text())
        self.clients = []; self.admin_token = None; self.transport = None;self.admin_refresh=None;self.owned={}

    @property
    def issuer(self):return f"{self.base}/realms/{self.realm}"

    def admin_login(self):
        if self.admin_refresh:
            self.admin_http.call("POST",self.base+"/realms/master/protocol/openid-connect/logout",form={"client_id":"admin-cli","refresh_token":self.admin_refresh})
        answer = required(self.admin_http.call("POST", self.base + "/realms/master/protocol/openid-connect/token", form={
            "grant_type": "password", "client_id": "admin-cli", "username": self.credentials["keycloak_admin"], "password": self.credentials["keycloak_password"]}))
        self.admin_token = answer["access_token"]
        self.admin_refresh=answer.get("refresh_token")

    def admin(self, method, path, payload=None):
        if self.admin_token is None:self.admin_login()
        return self.admin_http.call(method, self.base + "/admin/realms" + path, payload=payload, headers={"Authorization": "Bearer " + self.admin_token})

    def setup(self):
        self.admin_login(); existing = self.admin("GET", "/" + self.realm)
        if existing["http"] == 404:
            required(self.admin("POST", "", {"realm": self.realm, "enabled": True, "sslRequired": "none", "registrationAllowed": False,
                "accessTokenLifespan": 300, "ssoSessionIdleTimeout": 1800, "ssoSessionMaxLifespan": 3600,
                "revokeRefreshToken": True, "refreshTokenMaxReuse": 0, "eventsEnabled": True,
                "attributes": {"research-owned": "auth-lifecycle-local-only"}}), 201)
        elif existing["http"] != 200 or existing["body"].get("attributes", {}).get("research-owned") != "auth-lifecycle-local-only":
            raise NativeError("refusing to use an unowned realm")
        for index in range(2):
            cid = f"l1-client-{index}"; found = required(self.admin("GET", f"/{self.realm}/clients?clientId={cid}"))
            if not found:
                required(self.admin("POST", f"/{self.realm}/clients", {"clientId": cid, "enabled": True, "publicClient": False,
                    "directAccessGrantsEnabled": True, "standardFlowEnabled": True, "serviceAccountsEnabled": False,
                    "redirectUris": ["http://127.0.0.1:18083/callback"], "protocol": "openid-connect", "fullScopeAllowed": False}), 201)
                found = required(self.admin("GET", f"/{self.realm}/clients?clientId={cid}"))
            secret = required(self.admin("GET", f"/{self.realm}/clients/{found[0]['id']}/client-secret"))["value"]
            mappers = required(self.admin("GET", f"/{self.realm}/clients/{found[0]['id']}/protocol-mappers/models"))
            if not any(x.get("name") == "l1-explicit-audience" for x in mappers):
                required(self.admin("POST", f"/{self.realm}/clients/{found[0]['id']}/protocol-mappers/models", {
                    "name": "l1-explicit-audience", "protocol": "openid-connect", "protocolMapper": "oidc-audience-mapper",
                    "config": {"included.client.audience": cid, "access.token.claim": "true", "introspection.token.claim": "true", "id.token.claim": "false"}}), 201)
            self.clients.append({"id": cid, "secret": secret, "native_id": found[0]["id"]})
        return self.discovery()

    def discovery(self):return required(self.http.call("GET", self.issuer + "/.well-known/openid-configuration"))

    def create_actor(self, name):
        if not name.startswith("l1-"):raise NativeError("only owned test actors")
        password = secrets.token_urlsafe(22)
        response = self.admin("POST", f"/{self.realm}/users", {"username": name, "enabled": True, "emailVerified": True,
            "firstName": "Study", "lastName": "Fixture", "email": name + "@example.invalid",
            "credentials": [{"type": "password", "value": password, "temporary": False}]})
        required(response, 201)
        users = required(self.admin("GET", f"/{self.realm}/users?username={urllib.parse.quote(name)}&exact=true"))
        self.owned[name]=users[0]["id"]
        return {"name": name, "password": password, "id": users[0]["id"]}

    def check_actor(self,actor):
        if self.owned.get(actor["name"])!=actor["id"]:raise NativeError("actor not created by this owned test adapter")

    def _send(self, kind, method, url, **kwargs):
        if self.transport:return self.transport(kind, lambda: self.http.call(method, url, **kwargs))
        return self.http.call(method, url, **kwargs)

    def issue(self, actor, client=0):
        self.check_actor(actor)
        c = self.clients[client]
        return self._send("configure", "POST", self.issuer + "/protocol/openid-connect/token", form={"grant_type": "password",
            "client_id": c["id"], "client_secret": c["secret"], "username": actor["name"], "password": actor["password"], "scope": "openid"})

    def refresh(self, token, client=0):
        c = self.clients[client]
        return self._send("refresh", "POST", self.issuer + "/protocol/openid-connect/token", form={"grant_type": "refresh_token",
            "client_id": c["id"], "client_secret": c["secret"], "refresh_token": token})

    def introspect(self, token, client=0, hint="access_token"):
        c = self.clients[client]
        return self._send("probe", "POST", self.issuer + "/protocol/openid-connect/token/introspect", form={
            "client_id": c["id"], "client_secret": c["secret"], "token": token, "token_type_hint": hint})

    def revoke(self, token, client=0, hint="refresh_token"):
        c = self.clients[client]
        return self._send("stop", "POST", self.issuer + "/protocol/openid-connect/revoke", form={
            "client_id": c["id"], "client_secret": c["secret"], "token": token, "token_type_hint": hint})

    def root_stop(self, actor):
        self.check_actor(actor)
        call = lambda: self.admin("POST", f"/{self.realm}/users/{actor['id']}/logout")
        response=self.transport("cleanup", call) if self.transport else call();required(response,204);return response

    def remove_actor(self, actor):
        self.check_actor(actor)
        response=self.admin("DELETE", f"/{self.realm}/users/{actor['id']}");required(response,204);self.owned.pop(actor["name"]);return response

    def native_sessions(self, actor):
        self.check_actor(actor);return required(self.admin("GET", f"/{self.realm}/users/{actor['id']}/sessions"))

    def set_rotation(self, enabled):
        return self.admin("PUT", "/" + self.realm, {"revokeRefreshToken": enabled, "refreshTokenMaxReuse": 0})

    def root_id(self, token):return claims(token).get("sid") or claims(token).get("session_state")


class Casdoor:
    name = "casdoor"; version = "4.25.0"; base = "http://127.0.0.1:18081"
    organization = "l1-study"
    native_record_kind = "oauth_token_record"
    root_action_kind = "disable_owned_test_account_and_expire_its_tokens"
    def __init__(self):
        self.http = HTTP(); self.admin_http = HTTP(cookies=True); self.clients = []; self.transport = None
        self.credentials = json.loads((PRIVATE/"secrets.json").read_text());self.logged_in=False;self.owned={}

    @property
    def issuer(self):return self.base

    def admin_login(self):
        if self.logged_in:return
        response = self.admin_http.call("POST", self.base + "/api/login", payload={"type": "login", "organization": "built-in",
            "username": "admin", "password": self.credentials["casdoor_password"], "application": "app-built-in", "autoSignin": True})
        body = required(response)
        if body.get("status") != "ok":raise NativeError("Casdoor admin login: " + str(body.get("msg", "failed")))
        self.logged_in=True

    def admin(self, method, path, payload=None):return self.admin_http.call(method, self.base + "/api/" + path, payload=payload)

    def setup(self):
        self.admin_login()
        org = required(self.admin("GET", "get-organization?id=admin/" + self.organization))
        if not org.get("data"):
            template_org = required(self.admin("GET", "get-organization?id=admin/built-in"))["data"]
            template_org.update(name=self.organization, displayName="Owned L1 study", isProfilePublic=False)
            response = required(self.admin("POST", "add-organization", template_org))
            if response.get("status") != "ok":raise NativeError("test organization creation failed")
        original = required(self.admin("GET", "get-application?id=admin/app-built-in"))
        if original.get("status") != "ok":raise NativeError("Casdoor application read failed")
        template = original["data"]
        for index in range(2):
            name = f"app-l1-{index}"; current = required(self.admin("GET", "get-application?id=admin/" + name))
            if not current.get("data"):
                app = deepcopy(template); app.update(name=name, displayName="Owned L1 research", clientId=f"l1-client-{index}", clientSecret=secrets.token_urlsafe(30),
                    redirectUris=["http://127.0.0.1:18083/callback"], enableSignUp=False, enablePassword=True,
                    organization=self.organization, grantTypes=["password", "refresh_token", "authorization_code"], expireInHours=1, refreshExpireInHours=1)
                created = required(self.admin("POST", "add-application", app))
                if created.get("status") != "ok":raise NativeError("Casdoor application create: " + str(created.get("msg")))
                current = required(self.admin("GET", "get-application?id=admin/" + name))
            app = current["data"]
            if app.get("organization") != self.organization:
                app["organization"] = self.organization
                updated = required(self.admin("POST", "update-application?id=admin/" + name, app))
                if updated.get("status") != "ok":raise NativeError("test application organization update failed")
            self.clients.append({"id": app["clientId"], "secret": app["clientSecret"], "native_id": app["name"], "configuration": app})
        return self.discovery()

    def discovery(self):return required(self.http.call("GET", self.base + "/.well-known/openid-configuration"))

    def create_actor(self, name):
        if not name.startswith("l1-"):raise NativeError("only owned test actors")
        password = secrets.token_urlsafe(22)
        actor = {"owner": self.organization, "name": name, "displayName": "Owned L1 fixture", "type": "normal-user", "password": password,
                 "email": name + "@example.invalid", "isAdmin": False, "isForbidden": False}
        body = required(self.admin("POST", "add-user", actor))
        if body.get("status") != "ok":raise NativeError("Casdoor add user: " + str(body.get("msg")))
        read = required(self.admin("GET", "get-user?id=" + self.organization + "/" + name))["data"]
        self.owned[name]=read["id"]
        return {"name": name, "password": password, "id": read["id"]}

    def check_actor(self,actor):
        if self.owned.get(actor["name"])!=actor["id"]:raise NativeError("actor not created by this owned test adapter")

    def _send(self, kind, method, url, **kwargs):
        if self.transport:return self.transport(kind, lambda: self.http.call(method, url, **kwargs))
        return self.http.call(method, url, **kwargs)

    def issue(self, actor, client=0):
        self.check_actor(actor)
        c = self.clients[client]
        return self._send("configure", "POST", self.base + "/api/login/oauth/access_token", form={"grant_type": "password",
            "client_id": c["id"], "client_secret": c["secret"], "username": actor["name"], "password": actor["password"], "scope": "openid"})

    def refresh(self, token, client=0):
        c = self.clients[client]
        return self._send("refresh", "POST", self.base + "/api/login/oauth/refresh_token", form={"grant_type": "refresh_token",
            "client_id": c["id"], "client_secret": c["secret"], "refresh_token": token, "scope": "openid"})

    def introspect(self, token, client=0, hint="access_token"):
        c = self.clients[client]
        return self._send("probe", "POST", self.base + "/api/login/oauth/introspect", form={
            "client_id": c["id"], "client_secret": c["secret"], "token": token, "token_type_hint": hint})

    def revoke(self, token, client=0, hint="refresh_token"):
        c = self.clients[client]
        return self._send("stop", "POST", self.base + "/api/login/oauth/revoke", form={
            "client_id": c["id"], "client_secret": c["secret"], "token": token, "token_type_hint": hint})

    def root_stop(self, actor):
        self.check_actor(actor)
        call = lambda: self.admin("POST", "update-user?id=" + self.organization + "/" + actor["name"] + "&columns=isForbidden", {"owner": self.organization, "name": actor["name"], "isForbidden": True})
        response=self.transport("cleanup", call) if self.transport else call()
        if required(response).get("status")!="ok":raise NativeError("native owned-account stop failed")
        return response

    def remove_actor(self, actor):
        self.check_actor(actor)
        response=self.admin("POST", "delete-user", {"owner": self.organization, "name": actor["name"]})
        if required(response).get("status")!="ok":raise NativeError("native owned-user deletion failed")
        self.owned.pop(actor["name"]);return response

    def native_sessions(self, actor):
        # Native database rows, not a second custom authentication server.
        import sqlite3
        self.check_actor(actor)
        with sqlite3.connect("file:" + str(PRIVATE/"casdoor-l1.db") + "?mode=ro", uri=True) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute('SELECT name, application, user, expires_in, created_time FROM token WHERE user = ?', (actor["name"],))]

    def set_rotation(self, enabled):
        # Rotation policy is not assumed to be configurable through a guessed API.
        raise NativeError("Casdoor rotation change is not registered in this adapter")

    def root_id(self, token):
        import sqlite3
        from hashlib import sha256
        with sqlite3.connect("file:" + str(PRIVATE/"casdoor-l1.db") + "?mode=ro", uri=True) as conn:
            row = conn.execute('SELECT name FROM token WHERE access_token = ? OR access_token_hash = ?', (token, sha256(token.encode()).hexdigest())).fetchone()
        return row[0] if row else None


def connect(name):
    provider = {"keycloak": Keycloak, "casdoor": Casdoor}[name](); provider.setup(); return provider
