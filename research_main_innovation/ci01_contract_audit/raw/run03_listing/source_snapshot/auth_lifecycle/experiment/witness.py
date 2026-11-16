"""Independent native-effect witness; never trusts a method's completion flag."""
import base64
import json
import time
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from .providers import HTTP, required, claims
from .journal import fingerprint, read_verified


def decode(value):return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


class Witness:
    def __init__(self, provider, journal=None):
        self.provider = provider; self.journal = journal; self.http = HTTP(); self.cache = {}
        discovery = provider.discovery(); self.issuer = discovery["issuer"]; self.introspection_url = discovery["introspection_endpoint"]
        self.keys = required(self.http.call("GET", discovery["jwks_uri"]))["keys"]

    def signed_access(self, token, client=0, subject=None):
        try:
            head, data, sig = token.split("."); header = json.loads(decode(head)); payload = json.loads(decode(data))
            if header.get("alg") != "RS256":return False
            key = next(k for k in self.keys if k.get("kid") == header.get("kid") and k["kty"] == "RSA")
            public = rsa.RSAPublicNumbers(int.from_bytes(decode(key["e"]), "big"), int.from_bytes(decode(key["n"]), "big")).public_key()
            public.verify(decode(sig), (head + "." + data).encode(), padding.PKCS1v15(), hashes.SHA256())
            aud = payload.get("aud", []); aud = [aud] if isinstance(aud, str) else aud
            return (payload["iss"] == self.issuer and self.provider.clients[client]["id"] in aud and payload["exp"] > time.time()
                    and payload.get("nbf", 0) <= time.time() and (subject is None or payload.get("sub") == subject))
        except Exception:return False

    def active(self, token, client=0, hint="access_token"):
        c = self.provider.clients[client]
        r = self.http.call("POST", self.introspection_url, form={"token": token, "token_type_hint": hint, "client_id": c["id"], "client_secret": c["secret"]})
        value = r["body"].get("active") if r["http"] == 200 and type(r["body"].get("active")) is bool else None
        if self.journal:self.journal.emit("authority_witness", "witness", credential_ref=fingerprint(token), caller_client=client, hint=hint, active=value, http_status=r["http"], counted=False)
        return value

    def accepted(self, token, mode="online", *, client=0, subject=None, cache_ttl=30, query_client=None):
        signature = self.signed_access(token, client, subject)
        if not signature:return False
        if mode == "offline":return True
        query_client=client if query_client is None else query_client
        key = (fingerprint(token), query_client)
        if mode == "cached" and key in self.cache and self.cache[key][0] > time.monotonic():return self.cache[key][1]
        active = self.active(token, query_client)
        if mode == "cached":self.cache[key] = (time.monotonic()+cache_ttl, active)
        return active

    def native_unit(self, token, actor):
        identifier = self.provider.root_id(token)
        rows = self.provider.native_sessions(actor)
        matched = any(row.get("id", row.get("name")) == identifier for row in rows)
        if self.provider.name=="keycloak":
            client=claims(token).get("azp")
            matched=any(row.get("id")==identifier and client in row.get("clients",{}).values() for row in rows)
            identifier=str(identifier)+":"+str(client)
        return fingerprint(self.provider.name + ":" + str(identifier)) if identifier and matched else None


def request_cost(path):
    rows = read_verified(path)
    return sum(row["event"] == "request_sent" and row["payload"].get("counted") is True for row in rows)
