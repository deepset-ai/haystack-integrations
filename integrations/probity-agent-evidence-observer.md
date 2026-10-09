---
layout: integration
name: Probity Agent Evidence Observer
description: Keep signed file-write evidence and native Haystack traces together, then verify a record before publishing it.
authors:
  - name: Sankalp Gilda
    socials:
      github: astrogilda
repo: https://github.com/probityai/agent-evidence-observer
type: Monitoring Tool
report_issue: https://github.com/probityai/agent-evidence-observer/issues
version: Haystack 3.3.0
toc: true
---

## Overview

A tool can finish a write and then raise an error. If you only look at the
agent's final message, you can miss the effect that already happened.

Probity Agent Evidence Observer provides a source-installed reference integration
for Haystack `Pipeline`, `Agent`, and `Tool`. It connects a signed permission to
write exact bytes with the durable write history and Haystack's native trace.
A separately installed reader checks the retained records before releasing them
for publication.

The Haystack 3.3.0 profile includes seven runnable cases: a permitted write,
changed write content, errors before and after a write, a handled tool error,
step exhaustion, and a truncated response. The generator supplies scripted
replies, so you can run the whole profile without a model account or API key.

The integration includes:

- An `AuthorizedBroker` check inside the tool function, before the write occurs.
- Signed commitments, write history, and witness checkpoints for the file effect.
- Native model messages, tool calls, errors, trace ancestry, and span closure.
- A reader that checks the complete seven-case population without importing Haystack.
- A publication gate that releases the clean permitted record and retains the six
  fault cases without publishing them.

The reference covers one tool per step and local file writes. The
[profile contract](https://github.com/probityai/agent-evidence-observer/blob/1be320b6614da07bde513b237d61d59c85b91c8c/interop/haystack-native-2026-10-03/PROFILE.md)
sets out the measured cases, policy inputs, and observation coverage.

## Installation

Start from the tested source revision below. The runner builds both Observer and
the Haystack reference package as wheels, then installs separate producer and
reader environments with hash-locked dependencies.

You will need Git, Bash, `sha256sum`, and Python with `venv` support. The runner
uses `uv` 0.8.22 and Python 3.13; `uv` can download Python 3.13 if needed. The
reference CI runs on Ubuntu 24.04.

```bash
git clone https://github.com/probityai/agent-evidence-observer.git
cd agent-evidence-observer
git checkout --detach 1be320b6614da07bde513b237d61d59c85b91c8c

verification_root="$(mktemp -d)"
python3 -m venv "$verification_root/runner"
"$verification_root/runner/bin/python" -m pip install 'uv==0.8.22'

PATH="$verification_root/runner/bin:$PATH" \
  bash interop/haystack-native-2026-10-03/verify_install.sh \
  "$verification_root/evidence"
```

Keep `verification_root` in the same shell for the example below. The script
creates the `evidence` directory, runs 31 focused controls and all seven native
cases, and saves the original records, installed-source manifest, reader reports,
and released record there.

## Usage

The complete runner above produces two useful outputs:

- `evidence/reader-report.json` records every case, its tool calls, committed
  writes, native exit reason, and publication decision.
- `evidence/publication/published.json` contains only the clean permitted record.

To verify the saved population again and create a new publication, use the
separate reader environment:

```bash
policy_sha="$(sha256sum "$verification_root/evidence/packet/host-policy.json" | cut -d ' ' -f1)"

"$verification_root/evidence/reader/bin/python" -I -B \
  -m probity_haystack.reader "$verification_root/evidence/packet" \
  --host-policy "$verification_root/evidence/packet/host-policy.json" \
  --policy-sha256 "$policy_sha" \
  --publish "$verification_root/replayed-publication"
```

The publication directory must be new. A changed artifact, invalid signature,
missing case, or inconsistent native trace causes the reader to refuse before
creating it.

This example uses the policy created by the reference host. For a separate
consumer, supply the trusted policy and its digest through your own trusted
channel rather than accepting policy or keys chosen by a candidate record.

For the implementation, see the
[native Haystack producer](https://github.com/probityai/agent-evidence-observer/blob/1be320b6614da07bde513b237d61d59c85b91c8c/interop/haystack-native-2026-10-03/probity_haystack/producer.py)
and [installed reader](https://github.com/probityai/agent-evidence-observer/blob/1be320b6614da07bde513b237d61d59c85b91c8c/interop/haystack-native-2026-10-03/probity_haystack/reader.py).
The [passing native CI run](https://github.com/probityai/agent-evidence-observer/actions/runs/37139952519)
retains the complete verification artifacts.

## License

Probity Agent Evidence Observer and this reference integration use
[Apache-2.0](https://github.com/probityai/agent-evidence-observer/blob/1be320b6614da07bde513b237d61d59c85b91c8c/LICENSE).
