from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-zА-Яа-я]{2,}")
_JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]{20,}(?:\.[A-Za-z0-9_-]{10,}){1,2}\b")
_API_KEY_RE = re.compile(r"\bGPN\.[A-Za-z0-9.]{20,}\b")
_PHONE_RE = re.compile(r"\+?\d[\d()\- ,]{9,}\d")
_CARD_RE = re.compile(r"^\d{16,19}$")


def find_sensitive_values(value: Any, *, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child_path = f"{path}.{key}"
            low = str(key).lower()
            if low in {"api_key", "password", "password_hash"} and item not in {
                "<API_KEY>",
                "<SHA512_PASSWORD>",
            }:
                findings.append(f"{child_path}: sensitive key is not replaced")
            if low == "session_id" and item != "<SESSION_ID>":
                findings.append(f"{child_path}: session identifier is not replaced")
            if "email" in low and isinstance(item, str) and not item.endswith("@example.com"):
                findings.append(f"{child_path}: email is not anonymized")
            if (
                ("phone" in low or low == "mobile")
                and isinstance(item, str)
                and item != "79990000000"
            ):
                findings.append(f"{child_path}: phone is not anonymized")
            if (
                low in {"card_number", "number_card", "number"}
                and isinstance(item, str)
                and _CARD_RE.fullmatch(item)
                and item != "7000000000000000"
            ):
                findings.append(f"{child_path}: card number is not anonymized")
            findings.extend(find_sensitive_values(item, path=child_path))
        return findings
    if isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(find_sensitive_values(item, path=f"{path}[{index}]"))
        return findings
    if isinstance(value, str):
        if _JWT_RE.search(value):
            findings.append(f"{path}: JWT-like value")
        if _API_KEY_RE.search(value):
            findings.append(f"{path}: API-key-like value")
        for email in _EMAIL_RE.findall(value):
            if not email.endswith("@example.com"):
                findings.append(f"{path}: email {email!r} is not anonymized")
    return findings


def scan_text_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    findings: list[str] = []
    if _JWT_RE.search(text):
        findings.append(f"{path}: JWT-like value")
    if _API_KEY_RE.search(text):
        findings.append(f"{path}: API-key-like value")
    for email in _EMAIL_RE.findall(text):
        if not email.endswith("@example.com"):
            findings.append(f"{path}: email {email!r} is not anonymized")
    return findings
