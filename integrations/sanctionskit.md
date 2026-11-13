---
layout: integration
name: SanctionsKit
description: Explicitly scoped sanctions screening and retained evidence in Haystack pipelines.
authors:
  - name: SanctionsKit
    socials:
      github: SanctionsKit
repo: https://github.com/SanctionsKit/sanctionskit-haystack
report_issue: https://github.com/SanctionsKit/sanctionskit-haystack/issues
type: Custom Component
toc: true
version: Haystack 3.3
---

[SanctionsKit](https://www.sanctionskit.com/) provides a [sanctions screening API](https://www.sanctionskit.com/docs/screenings). This integration adds two components to Haystack pipelines:

- `SanctionsKitScreening` submits one screening with an explicitly selected source set or versioned package and a caller-provided idempotency key.
- `SanctionsKitResultReader` retrieves retained evidence for an existing result. It does not perform a new screening.

Both preserve the API's complete evidence object, including source versions, warnings, conflicts, matching policy and disclaimer. A potential match requires review. A no-match response applies only to the selected coverage and matching rules; it is not legal clearance.

## Installation

Use Python 3.10+ in a virtual environment. Install the tested source revision:

```sh
git clone https://github.com/SanctionsKit/sanctionskit-haystack.git
cd sanctionskit-haystack
git checkout aaf325c7e98d735347b0e9433b018110e6b071ae
python -m venv .venv
. .venv/bin/activate
python -m pip install .
```

This is a development version, with no published PyPI package. It supports Haystack 3.3.x. A fresh installation from this public revision passed all 42 tests with Python 3.12.14, Haystack 3.3.0 and synthetic HTTP fixtures; authenticated hosted execution has not been tested.

## Offline example

After installing from the source checkout, run `python examples/offline_screening.py`. This uses the real Haystack runtime with a synthetic response and local HTTP stub; it blocks network connections and needs no API key. It preserves the evidence for analyst review and makes no approval decision.

## Usage

Set `SANCTIONSKIT_API_KEY` using an environment variable or secret manager. Use a sandbox key for fictional examples. SanctionsKit's free sandbox uses synthetic data; production screening is paid.

```python
from haystack import Pipeline
from sanctionskit_haystack import SanctionsKitScreening

pipeline = Pipeline()
pipeline.add_component("screen", SanctionsKitScreening())
result = pipeline.run({
    "screen": {
        "request": {
            "subject": {"name": "Alex Morgan", "entityType": "person"},
            "package": "sandbox@1",
            "retention": "standard",
        },
        "idempotency_key": "haystack-fictional-example-001",
    }
})
evidence = result["screen"]["result"]
```

The screening key needs `screenings:write`. Supply exactly one of `sources` or `package`; the integration does not assume global coverage. Use a distinct idempotency key for each logical screening, and reuse it only for an identical retry. There are no automatic retries.

```python
from sanctionskit_haystack import SanctionsKitResultReader

retained = SanctionsKitResultReader().run(result_id=evidence["id"])["result"]
```

Retrieval needs `results:read`. Standard retention can retain submitted subject information. Minimal-retention evidence expires after 24 hours and omits submitted inputs. Review which information a pipeline passes to prompts, traces and document stores.

HTTP failures, uncertain transport outcomes and invalid evidence remain errors. They are never converted to a no-match result. Secrets are represented using Haystack's `Secret` class. To load trusted serialized pipelines under Haystack 3.3, allow this component module explicitly: `Pipeline.loads(yaml_text, allowed_modules=["sanctionskit_haystack.components"])`.

See the [public API reference](https://www.sanctionskit.com/docs/api-reference) for scopes, coverage and response evidence.

## License

The adapter is MIT licensed and maintained by SanctionsKit. The hosted API is governed separately by the [SanctionsKit terms](https://www.sanctionskit.com/terms) and [privacy policy](https://www.sanctionskit.com/privacy).
