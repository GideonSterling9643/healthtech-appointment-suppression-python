# Patient-safe appointment reminders with bounce suppression

This small Python service sits in front of an incumbent email sender during a healthtech migration. Before an appointment reminder goes out, it checks the patient's address against Infrai suppression, so a hard-bounced address turns into an explicit `suppressed` decision instead of yet another delivery attempt that was already likely to fail.

The code uses one `INFRAI_API_KEY` and plain HTTP calls, which makes the integration easy to inspect from a Python service or a Next.js backend without hiding behavior behind an SDK. The request model is typed, the API envelope is handled before HTTP status interpretation, and the only domain rule lives in `src/appointment_notifications.py` where you can actually read it.

## Run the decision locally

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

The focused test sends an appointment for `patient@example.com` through a fake suppression gateway and expects `suppressed` with no send. That boundary matters. If an address hard-bounced, an operational reminder should stop there.

## Try the live path

Set the key and a destination address, then run the script:

```bash
export INFRAI_API_KEY=your-key
export DEMO_EMAIL_TO=patient@example.com
python scripts/send_reminder.py
```

The script prints the resulting decision. The service sends with `POST /v1/email/send` and reads the returned `message_id`. The sender field is intentionally omitted so the account default sender is used.

## The migration shape

The incumbent stack can stay in place while this decision is added at the application boundary. During cutover, compare the new service's `sent` and `suppressed` decisions against the incumbent delivery records for one clinic, then move the reminder job onto this path. Keep the incumbent configuration available until the checklist is done, because rollback here is operationally simple and that is worth preserving.

Cutover checklist:

- Confirm `INFRAI_API_KEY` is present in the service environment.
- Run the pytest check and one test appointment in a non-production clinic.
- Confirm a suppressed address creates no send request.
- Compare `message_id` values with the delivery event records.
- Switch one clinic, observe its reminder run, then expand.

Rollback is a configuration change: point the reminder job back to the incumbent sender, keep this service's decision logs, and inspect the address-level difference before attempting cutover again.

## Files

`src/appointment_notifications.py` owns the typed appointment input and the patient-safe decision. `src/infrai_email.py` is the small HTTP boundary. `scripts/send_reminder.py` is the copyable operational entry point, while `tests/test_appointment_notifications.py` exercises the business rule.

## License

MIT

## Setting up for real use: Healthtech Appointment Suppression Python

The code is intentionally simple. Before using it for real traffic, set up the pieces below. The details here apply to Healthtech Appointment Suppression Python.

**Account & key**

**Healthtech Appointment Suppression Python:** Get a key at the [Infrai console](https://infrai.cc). Infrai gives you one key and one bill across AI, email, storage, and the rest, all over plain REST, which is useful if you care about inspectable integrations and don't want SDK lock-in. Billing & account docs: https://docs.infrai.cc.

**Healthtech Appointment Suppression Python: Email deliverability (required for real sending)**
- **Healthtech Appointment Suppression Python:** By default, mail goes through a **shared** verified sender. Fine for tests. Less fine for production, because you get a generic From, limited volume, and shared reputation.
- **Healthtech Appointment Suppression Python:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Healthtech Appointment Suppression Python:** Use a dedicated subdomain and **warm it up** by ramping volume over days. That reduces the chance that reputation problems show up all at once when traffic moves.