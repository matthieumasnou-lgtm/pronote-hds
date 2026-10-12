"""Experimental CAS/Keycloak connector for Mon College Hauts-de-Seine.

Only the school's official HTTPS login is used. No browser cookies, QR codes,
CAPTCHAs or multi-factor authentication are bypassed. Credentials are never logged.
This module is loaded only when the user explicitly chooses enc_hauts_de_seine.
"""
from __future__ import annotations
import re
from urllib.parse import urljoin, urlsplit
import requests
from bs4 import BeautifulSoup
from pronotepy.exceptions import ENTLoginError

ENT_HOST = "enc.hauts-de-seine.fr"
PRONOTE_SUFFIX = ".index-education.net"
TIMEOUT_SECONDS = 18

def _is_pronote_response(url: str, expected_host: str) -> bool:
    parsed = urlsplit(url)
    return (parsed.scheme == "https" and (parsed.hostname or "").lower() == expected_host
            and parsed.path.startswith("/pronote/"))

def _login_form(response):
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.find("form", id="kc-form-login")

def _safe_action(login_url: str, action: str) -> str:
    target = urljoin(login_url, action)
    parsed = urlsplit(target)
    if (parsed.scheme != "https" or parsed.hostname != ENT_HOST
            or not parsed.path.startswith("/auth/realms/oze_hds/")):
        raise ENTLoginError("Formulaire de connexion ENT non fiable : action externe refusee.")
    return target

def _login_payload(form, username: str, password: str) -> dict[str, str]:
    inputs = form.find_all("input", attrs={"name": True})
    names = {element.get("name") for element in inputs}
    if "username" not in names or "password" not in names:
        raise ENTLoginError("Champs identifiants non reconnus sur le portail ENT.")
    payload = {}
    for element in inputs:
        name = element["name"]
        kind = (element.get("type") or "text").lower()
        if kind in {"submit", "button", "file", "image"}:
            continue
        if kind in {"checkbox", "radio"} and not element.has_attr("checked"):
            continue
        payload[name] = element.get("value", "")
    payload["username"] = username
    payload["password"] = password
    return payload

def _follow_cas_redirects(session, response, pronote_host: str):
    """Follow safe GET redirects; never replay passwords on 307/308."""
    for _ in range(12):
        if response.status_code in (307, 308):
            raise ENTLoginError("Redirection CAS preservant le mot de passe refusee.")
        if response.status_code not in (301, 302, 303):
            return response
        location = response.headers.get("Location", "")
        next_url = urljoin(response.url, location)
        target = urlsplit(next_url)
        if target.scheme != "https" or target.hostname not in {ENT_HOST, pronote_host}:
            raise ENTLoginError("Redirection CAS externe non autorisee.")
        response = session.get(next_url, timeout=TIMEOUT_SECONDS, allow_redirects=False)
    raise ENTLoginError("Trop de redirections CAS consecutives.")

def enc_hauts_de_seine(
    username: str, password: str, pronote_url: str = "", **_kwargs
) -> requests.cookies.RequestsCookieJar:
    """Authenticate via ENC Keycloak/CAS and return scoped cookies."""
    page = urlsplit(pronote_url)
    expected_host = (page.hostname or "").lower()
    if (page.scheme != "https" or not expected_host.endswith(PRONOTE_SUFFIX)
            or not page.path.startswith("/pronote/")):
        raise ENTLoginError("URL Pronote non valide (URL HTTPS index-education attendue).")
    if not username or not password:
        raise ENTLoginError("Identifiant et mot de passe ENT obligatoires.")
    with requests.Session() as session:
        session.headers.update(
            {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Firefox/128.0"}
        )
        try:
            page_response = session.get(pronote_url, timeout=TIMEOUT_SECONDS)
            page_response.raise_for_status()
            parsed_login = urlsplit(page_response.url)
            if (parsed_login.scheme != "https" or parsed_login.hostname != ENT_HOST
                    or not parsed_login.path.startswith("/auth/realms/oze_hds/")):
                raise ENTLoginError(
                    "Pronote ne redirige pas vers la connexion CAS Hauts-de-Seine attendue."
                )
            form = _login_form(page_response)
            if form is None:
                raise ENTLoginError(
                    "Formulaire ENC introuvable : connexion EduConnect, MFA ou portail modifie."
                )
            if not form.get("action"):
                raise ENTLoginError("Action du formulaire ENT absente.")
            action = _safe_action(page_response.url, form["action"])
            payload = _login_payload(form, username, password)
            response = session.post(
                action, data=payload,
                headers={"Referer": page_response.url, "Origin": f"https://{ENT_HOST}"},
                timeout=TIMEOUT_SECONDS, allow_redirects=False,
            )
            response = _follow_cas_redirects(session, response, expected_host)
            response.raise_for_status()
            if not _is_pronote_response(response.url, expected_host):
                response = session.get(pronote_url, timeout=TIMEOUT_SECONDS)
                response.raise_for_status()
            if not _is_pronote_response(response.url, expected_host):
                if urlsplit(response.url).hostname == ENT_HOST and _login_form(response):
                    raise ENTLoginError(
                        "Authentification ENT refusee, ou une validation additionnelle est requise."
                    )
                raise ENTLoginError(
                    "Connexion ENT non finalisee : Pronote n'a pas recu la session CAS."
                )
            if not re.search(r"Start\s*\(\s*\{", response.text):
                raise ENTLoginError("Retour sur Pronote, mais page attendue non reconnue.")
            return session.cookies.copy()
        except requests.RequestException as exc:
            raise ENTLoginError("Erreur reseau HTTPS pendant la connexion a l'ENT.") from exc
