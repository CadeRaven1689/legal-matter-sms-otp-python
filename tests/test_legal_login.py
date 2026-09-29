from legal_login import InfraiClient, MatterIntake, complete_login


def test_verified_login_releases_document_and_deadline(monkeypatch):
    client = InfraiClient(api_key="test-key", base_url="http://test")
    seen = {}

    def fake_request(method, path, payload):
        seen.update(method=method, path=path, payload=payload)
        return {"verified": True}

    monkeypatch.setattr(client, "_request", fake_request)
    matter = MatterIntake("MAT-7", "Sam Rivera", "+15551234567", "https://example.test/doc/MAT-7", "2026-10-14")

    result = complete_login(client, matter, "481902")

    assert result.verified is True
    assert result.document_url.endswith("MAT-7")
    assert result.follow_up_deadline == "2026-10-14"
    assert seen == {"method": "POST", "path": "/v1/sms/verify", "payload": {"to": matter.phone, "code": "481902"}}


def test_missing_verification_does_not_release_protected_data(monkeypatch):
    client = InfraiClient(api_key="test-key", base_url="http://test")
    monkeypatch.setattr(client, "verify_code", lambda phone, code: {})
    matter = MatterIntake("MAT-7", "Sam Rivera", "+15551234567", "https://example.test/doc/MAT-7", "2026-10-14")

    result = complete_login(client, matter, "481902")

    assert result.verified is False
    assert result.document_url is None
    assert result.follow_up_deadline is None
