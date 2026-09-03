# MOU Python SDK Sample

A minimal example showing how to use the `mouclient` Python SDK to request
and consume consented personal data (permanent residency information) from
a Solid POD via the MOU (Personal Data Management) service ecosystem.

This is a lab/experimentation repo from our work during the MOU project —
shared as a sample, not as a supported product.

## What is MOU?

**MOU (Manažment osobných údajov / Personal Data Management)** is a
national Slovak e-government project run under MIRRI SR (the Ministry of
Investments, Regional Development and Informatization). It implements the
"MyData" concept: giving citizens a central place to see which public
administration systems hold their personal data, monitor who has accessed
it, and grant or revoke consent for that data to be shared with third
parties (e.g. other public services or private companies) for building
modern digital services. Under the hood, MOU stores and shares this
personal data using **Solid PODs** (decentralized personal data stores).

## About this sample

The client in this repo (`mouclient`) was **built on purpose by us
(Alistiq)** as an example integration against the MOU ecosystem.

MOU layers custom security and authentication on top of the Community
Solid Server it's built on — consent flows, verifiable credentials, and
encrypted POD access that go beyond the vanilla Solid protocol. That's why
a plain/generic Solid client can't be used as-is, and a custom SDK like
this one is needed to talk to MOU-provided PODs.

**This is a demo, not a production-ready client or SDK.** It's a
proof-of-concept from our exploration of the MOU integration surface, kept
intentionally minimal. It is also not useful on its own: it requires the
matching MOU backend/service counterpart, which is **not publicly
available**.

## Structure

- `python-sample/mouclient/` — the SDK client library (IAM login, POD access,
  consent/verifiable-credential flows, decryption, notifications).
- `python-sample/mou_repository.py` — a higher-level repository that parses
  the RDF/JSON-LD dataset returned by the SDK into plain Python objects.
- `python-sample/main.py` — end-to-end usage example: request access, wait
  for consent, then extract personal data.

## Setup

```bash
cd python-sample
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# fill in MOU_HOST, MOU_USER_NAME, MOU_SERVICE_NAME, MOU_SERVICE_SECRET, MOU_WALLET_PASSWORD
python main.py
```

All configuration is read from `.env` at runtime (see `.env.example` for the
full list of variables). Never commit a populated `.env` file — it contains
your service credentials.

## License

MIT — see [LICENSE](LICENSE).
