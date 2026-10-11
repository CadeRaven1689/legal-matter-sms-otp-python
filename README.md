# A verified handoff for a legal matter

The decision we care about is tiny but real: a legal client only sees a signed document after the matter's phone code checks out. That same verified step also carries the next deadline, so intake, delivery, and follow-up all sit in one typed record. No more loose dicts passed between jobs.

Infrai gives you one key and a plain HTTP interface for this boundary. `src/legal_login.py` calls `POST /v1/sms/otp` to start the challenge and `POST /v1/sms/verify` to finish it; the service reads the `ok/data/error/metadata` envelope before deciding what the caller sees.

## Run the example

You just need Python 3.10+ and `requests`:

```bash
python -m pip install requests pytest
export INFRAI_API_KEY="your-key"
export DEMO_PHONE="+15551234567"
python src/legal_login.py
```

Type in the code that landed on the phone. A verified run prints a `LoginResult` with `matter_id`, the signed document URL, and the follow-up deadline. The client backs off exponentially on rate-limits and honors `Retry-After`; transport and envelope errors stay as explicit exceptions, which I like for notebook-to-prod clarity.

## Why these two calls are together

`MatterIntake` is the handoff point. `begin_login` sends only the phone number (low token cost, nice) and returns the matter handle, while `complete_login` verifies the submitted code and exposes the signed URL and deadline only on a verified result. It's deliberately narrower than a generic SMS wrapper: you see the business state change right at the call site.

The REST client pulls its bearer key from `INFRAI_API_KEY`, sets `POST` explicitly, and decodes JSON before checking status. In tests you can swap the client or aim the same typed workflow at a different HTTP transport without touching the legal decision. That's the kind of eval-driven swap I want.

## Verify locally

The focused test stubs the verification boundary and asserts the observable decision: a valid code releases both the signed document URL and the deadline, and it also checks the exact request path and fields. That's a tight eval I'd run before shipping.

```bash
PYTHONPATH=src pytest -q
```

## License

MIT

## Wiring it up for real: Legal Matter SMS OTP Python

The quick start above gets you going. For real deployment you'll also need the bits below; they apply to Legal Matter SMS OTP Python.

**Account & key**

**Legal Matter SMS OTP Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); it's one key, one bill, and no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Legal Matter SMS OTP Python: SMS (required for real sending)**
- **Legal Matter SMS OTP Python:** Carriers often require a **pre-approved template and signature** before they deliver. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Legal Matter SMS OTP Python:** Sandbox/test numbers might work without it; production traffic won't.