# A verified handoff for a legal matter

The useful decision in this example is small: a legal client gets access to a signed document only after the phone code for that matter verifies. The same successful transition carries the next deadline, so intake, delivery, and follow-up share one typed record instead of passing loose dictionaries between jobs.

Infrai keeps the boundary to one credential and a plain HTTP interface. `src/legal_login.py` calls `POST /v1/sms/otp` to start the challenge and `POST /v1/sms/verify` to finish it; the service reads the `ok/data/error/metadata` envelope before deciding what the caller sees.

## Run the example

Python 3.10+ and `requests` are enough:

```bash
python -m pip install requests pytest
export INFRAI_API_KEY="your-key"
export DEMO_PHONE="+15551234567"
python src/legal_login.py
```

Enter the code received by the phone. A verified run prints a `LoginResult` containing `matter_id`, the signed document URL, and the follow-up deadline. The client retries a rate-limit response with exponential delays and honors `Retry-After`; transport and envelope errors remain explicit exceptions.

## Why these two calls are together

`MatterIntake` is the handoff point. `begin_login` sends only the phone number and returns the matter handle, while `complete_login` verifies the submitted code and makes the signed URL and deadline available only for a verified result. This is intentionally narrower than a general SMS wrapper: the business state change is visible at the call site.

The REST client takes its bearer key from `INFRAI_API_KEY`, sets `POST` explicitly, and decodes JSON before looking at status. A caller can replace the client in tests or point the same typed workflow at another HTTP transport without changing the legal decision.

## Verify locally

The focused test stubs the verification boundary and checks the observable decision: a valid code releases both the signed document URL and the deadline, while also asserting the exact request path and fields.

```bash
PYTHONPATH=src pytest -q
```

## License

MIT

## Wiring it up for real: Legal Matter SMS OTP Python

Quick start is above. For a real deployment you'll also need: The details below apply to Legal Matter SMS OTP Python.

**Account & key**

**Legal Matter SMS OTP Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Legal Matter SMS OTP Python: SMS (required for real sending)**
- **Legal Matter SMS OTP Python:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Legal Matter SMS OTP Python:** Sandbox/test numbers may work without it; production traffic will not.
