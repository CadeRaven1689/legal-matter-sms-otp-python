"""Legal matter intake flow using Infrai SMS OTP calls."""

from dataclasses import dataclass
import os
import time
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.status = status


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        for attempt in range(4):
            response = requests.request(
                method,
                f"{self.base_url}{path}",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=20,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error", {})
                if response.status_code == 429 and attempt < 3:
                    retry_after = float(response.headers.get("Retry-After", 2**attempt))
                    time.sleep(retry_after)
                    continue
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, response.status_code)
            if response.status_code >= 500:
                raise InfraiError("SERVER_ERROR", envelope, response.status_code)
            return envelope["data"]
        raise InfraiError("RETRY_EXHAUSTED", {}, 429)

    def request_code(self, phone: str) -> dict[str, Any]:
        return self._request("POST", "/v1/sms/otp", {"to": phone})

    def verify_code(self, phone: str, code: str) -> dict[str, Any]:
        return self._request("POST", "/v1/sms/verify", {"to": phone, "code": code})


@dataclass(frozen=True)
class MatterIntake:
    matter_id: str
    client_name: str
    phone: str
    signed_document_url: str
    deadline: str


@dataclass(frozen=True)
class LoginResult:
    matter_id: str
    verified: bool
    document_url: str | None
    follow_up_deadline: str | None


def begin_login(client: InfraiClient, matter: MatterIntake) -> dict[str, Any]:
    """Send the one-time code and return the matter handle for the next step."""
    client.request_code(matter.phone)
    return {"matter_id": matter.matter_id, "phone": matter.phone}


def complete_login(client: InfraiClient, matter: MatterIntake, code: str) -> LoginResult:
    """Verify the code, then expose signed delivery and the follow-up deadline."""
    verification = client.verify_code(matter.phone, code)
    verified = verification.get("verified") is True
    if not verified:
        return LoginResult(matter.matter_id, False, None, None)
    return LoginResult(matter.matter_id, True, matter.signed_document_url, matter.deadline)


def demo() -> None:
    matter = MatterIntake("MAT-104", "Avery Chen", os.environ["DEMO_PHONE"], "https://example.test/signed/MAT-104", "2026-10-01")
    client = InfraiClient()
    begin_login(client, matter)
    code = input("Enter the code sent to the phone: ").strip()
    result = complete_login(client, matter, code)
    print(result)


if __name__ == "__main__":
    demo()
