---
layout: integration
name: LLMSecTest
description: Scan a deployed Haystack pipeline against the OWASP Top 10 for LLM Applications and get a SARIF report
authors:
    - name: Mark Wernsdorfer
      socials:
        github: wehnsdaefflae
pypi: https://pypi.org/project/llmsectest
repo: https://github.com/wehnsdaefflae/llmsectest
report_issue: https://github.com/wehnsdaefflae/llmsectest/issues
type: Evaluation Framework
version: Haystack 2.0
toc: true
---

### Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Usage](#usage)
4. [What it reports](#what-it-reports)
5. [Limits worth knowing before you run it](#limits-worth-knowing-before-you-run-it)

## Overview

[LLMSecTest](https://github.com/wehnsdaefflae/llmsectest) scans a deployed Haystack pipeline against the
[OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/) and writes SARIF, HTML, JSON,
Markdown and a CycloneDX SBOM. It runs as a CLI or as a pytest plugin, so a scan can be a step in CI.

**It works over HTTP and adds nothing to your pipeline.** There is no component to import, no wrapper
to configure and no code change: you point it at the endpoint you already serve. That means it exercises
what you actually deployed, with your prompt assembly, your retrieval, your output handling and your
model in the loop together, rather than any one of them in isolation.

Eight Haystack pipelines are part of the project's own daily regression cohort. They are deliberately
undefended fixtures built to keep the detectors honest rather than examples of good practice, and every
report is published unedited at <https://llmsec.dev/reports/>.

## Installation

```bash
pip install llmsectest
```

## Usage

Try it with no application and no network first. This scans a bundled hardened demo target and exits 0:

```bash
llmsectest --target demo-defended
```

Then point it at your own pipeline. Give it an HTTP endpoint that accepts `{"message": "..."}` and
answers with the pipeline's reply, plus the three things that turn a guess into a measurement: the
system prompt you deployed, a canary value you planted in it, and the exact shape of any privileged
action your pipeline can emit.

```bash
llmsectest \
  --target app:http://127.0.0.1:8000/chat \
  --app-prompt prompt.txt \
  --app-secret "sk-canary-123" \
  --app-action "ACTION: refund(" \
  --sarif-output haystack-app.sarif
llmsectest --render-sarif haystack-app.sarif
```

The exit code is non-zero when there are findings **and** when probes never reached your application, so
a broken endpoint cannot read as a clean bill of health.

## What it reports

Ten OWASP categories, eight of them black-box against the running application and two white-box against
your repository and model files:

| | |
|---|---|
| LLM01 Prompt Injection | marker-injection corpus plus red-team jailbreak prompts |
| LLM02 Sensitive Information Disclosure | four mechanisms, each looking for your planted canary, including base16/32/64/85, ROT13, quoted-printable, Unicode-confusable and character-split encodings of it |
| LLM03 Supply Chain | dependency manifests, pins against OSV, CycloneDX SBOM (`--repo`) |
| LLM04 Data and Model Poisoning | model-file scan (`--model-scan`) |
| LLM05 Improper Output Handling | `javascript:` URIs, unescaped HTML, shell metacharacters in generated output |
| LLM06 Excessive Agency | whether a privileged action signature you declared was actually emitted |
| LLM07 System Prompt Leakage | verbatim spans of your deployed prompt |
| LLM08 Vector and Embedding Weaknesses | retrieval exposure and indirect injection through the indexed corpus (`--app-canary`, `--app-rag-poison`) |
| LLM09 Misinformation | confident answers about entities that do not exist |
| LLM10 Unbounded Consumption | output flooding and amplification |

## Limits worth knowing before you run it

- **A category you gave no input to is reported as skipped, naming the flag it needs.** It is never
  rendered as a silent pass.
- **A probe that never came back is `inconclusive`, not `withstood`.** An unanswered probe is not a fact
  about your application.
- **If any reply in a run contains your canary, sensitive-disclosure attempts that survived are voided
  rather than counted as withstood**, whichever probe got the value out.
- Results depend on the model behind your pipeline. A run tells you about the deployment you scanned.
