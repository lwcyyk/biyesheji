"""Typed material bundles with legacy synthetic-string compatibility."""

import base64
import json
import time

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from .protocol import InvalidInput, digest, exact_fields, identifier


def validate_material(material, account=None, client=None):
    if isinstance(material, str):
        if not 1 <= len(material) <= 4096:
            raise InvalidInput("INVALID_LEGACY_MATERIAL")
        return material
    if not isinstance(material, dict) or material.get("schema") != 2:
        raise InvalidInput("INVALID_MATERIAL_SCHEMA")
    kind = material.get("kind")
    if kind == "casdoor_login":
        exact_fields(material, ("schema", "kind", "issuer", "client", "expected_account", "username", "password"))
        identifier(material["username"])
        if not isinstance(material["password"], str) or not material["password"]:
            raise InvalidInput("MISSING_LOGIN_SECRET")
    elif kind == "casdoor_oauth":
        exact_fields(material, ("schema", "kind", "issuer", "client", "expected_account", "native", "derived"))
        native = material["native"]
        exact_fields(native, ("access_token", "refresh_token", "token_type", "scope", "expires_in", "id_token"))
        for field in ("access_token", "refresh_token"):
            if not isinstance(native[field], str) or not 1 <= len(native[field]) <= 32768:
                raise InvalidInput("MISSING_TOKEN")
        if (not isinstance(native["token_type"], str) or native["token_type"].lower() != "bearer" or type(native["expires_in"]) is not int
                or native["expires_in"] <= 0):
            raise InvalidInput("INVALID_TOKEN_METADATA")
        claims = material["derived"].get("verified_claims", {})
        audience = claims.get("aud", [])
        audience = [audience] if isinstance(audience, str) else audience
        if claims.get("sub") != material["expected_account"] or material["client"] not in audience:
            raise InvalidInput("CLAIM_BINDING_MISMATCH")
        if claims.get("iss") != material["issuer"]:
            raise InvalidInput("ISSUER_MISMATCH")
    else:
        raise InvalidInput("INVALID_MATERIAL_KIND")
    if material["issuer"] != "http://127.0.0.1:18081":
        raise InvalidInput("UNREGISTERED_ISSUER")
    identifier(material["client"])
    identifier(material["expected_account"])
    if account is not None and material["expected_account"] != account:
        raise InvalidInput("MATERIAL_ACCOUNT_MISMATCH")
    if client is not None and material["client"] != client:
        raise InvalidInput("MATERIAL_CLIENT_MISMATCH")
    return material


def decode64(value):
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def verified_claims(token, profile, fallback_kid=None):
    try:
        head, body, signature = token.split(".")
        header = json.loads(decode64(head))
        claims = json.loads(decode64(body))
        if header.get("alg") != "RS256":
            raise ValueError("ALGORITHM")
        key_id = header.get("kid") or fallback_kid
        key = next(k for k in profile["jwks"]["keys"] if k.get("kid") == key_id and k.get("kty") == "RSA")
        public = rsa.RSAPublicNumbers(int.from_bytes(decode64(key["e"]), "big"),
                                     int.from_bytes(decode64(key["n"]), "big")).public_key()
        public.verify(decode64(signature), (head + "." + body).encode(), padding.PKCS1v15(), hashes.SHA256())
        aud = claims.get("aud", [])
        aud = [aud] if isinstance(aud, str) else aud
        if (claims.get("iss") != profile["base"] or claims.get("sub") != profile["actor"]["id"]
                or profile["client_id"] not in aud or claims.get("exp", 0) <= time.time()
                or claims.get("nbf", 0) > time.time()):
            raise ValueError("BINDING")
        return claims
    except Exception as error:
        raise InvalidInput("NATIVE_TOKEN_VERIFICATION_FAILED") from error


def token_bundle(body, profile):
    for name in ("access_token", "refresh_token", "token_type", "expires_in"):
        if name not in body:
            raise InvalidInput("NATIVE_RESPONSE_MISSING_FIELD")
    claims = verified_claims(body["access_token"], profile)
    access_header = json.loads(decode64(body["access_token"].split(".")[0]))
    refresh_claims = verified_claims(body["refresh_token"], profile, access_header.get("kid"))
    material = {"schema": 2, "kind": "casdoor_oauth", "issuer": profile["base"],
                "client": profile["client_id"], "expected_account": profile["actor"]["id"],
                "native": {key: body.get(key) for key in
                           ("access_token", "refresh_token", "token_type", "scope", "expires_in", "id_token")},
                "derived": {"verified_claims": claims, "verified_refresh_claims": refresh_claims,
                            "access_ref": digest(body["access_token"]),
                            "refresh_ref": digest(body["refresh_token"]), "requested_scope": "openid",
                            "native_identifier_claim": claims.get("jti"),
                            "identifier_status": "JWT_CLAIM_REQUIRES_NATIVE_UNIT_MAPPING"}}
    return validate_material(material, profile["actor"]["id"], profile["client_id"])
