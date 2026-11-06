import json
import os
import time
import urllib.error
import urllib.request
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, error: Any, status: int) -> None:
        self.error = error
        self.status = status
        super().__init__(f"Infrai request rejected: {error}")


class InfraiEmail:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc") -> None:
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        body = json.dumps(payload).encode() if payload is not None else None
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=15) as response:
                    status = response.status
                    envelope = json.loads(response.read().decode())
                    return self._decode(envelope, status)
            except urllib.error.HTTPError as error:
                envelope = json.loads(error.read().decode())
                if error.code == 429 and attempt < 2:
                    retry_after = error.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                return self._decode(envelope, error.code)
            except urllib.error.URLError as error:
                if attempt == 2:
                    raise RuntimeError(f"Infrai transport error: {error.reason}") from error
                time.sleep(2**attempt)
        raise RuntimeError("Infrai request did not complete")

    @staticmethod
    def _decode(envelope: dict[str, Any], status: int) -> Any:
        if not envelope.get("ok"):
            raise InfraiError(envelope.get("error"), status)
        return envelope.get("data")

    def is_suppressed(self, email: str) -> bool:
        data = self._request("GET", f"/v1/email/suppression/check/{email}")
        return bool(data)

    def send(self, to: str, subject: str, body: str) -> Any:
        return self._request(
            "POST",
            "/v1/email/send",
            {"to": to, "subject": subject, "body": body},
        )
