---
layout: integration
name: Inkog
description: Scan Haystack agent code for security vulnerabilities — prompt injection, infinite loops, missing guardrails, and more
authors:
    - name: Inkog
      socials:
        github: inkog-io
        linkedin: https://www.linkedin.com/company/inkog
repo: https://github.com/inkog-io/inkog
type: Security Tool
report_issue: https://github.com/inkog-io/inkog/issues
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [What It Detects](#what-it-detects)
- [License](#license)

## Overview

[Inkog](https://github.com/inkog-io/inkog) is an open-source security scanner for AI agent code. It performs static analysis to detect behavioral vulnerabilities such as prompt injection, infinite loops, token bombing, SQL injection via LLM, and missing human oversight.

Inkog understands Haystack pipelines and components natively — it parses your agent code and maps findings to compliance frameworks including OWASP LLM Top 10, EU AI Act, and NIST AI RMF.

Available as a CLI, MCP server (for Claude and Cursor), and GitHub Action.

## Installation

**CLI (via Homebrew):**
```bash
brew install inkog-io/tap/inkog
```

**MCP server (via npm):**
```bash
npx -y @inkog-io/mcp
```

**Or download from [GitHub Releases](https://github.com/inkog-io/inkog/releases).**

## Usage

### Scan a Haystack project

```bash
inkog -path /path/to/your/haystack/project
```

Example output:

```
CRITICAL  prompt_injection
          Pipeline component accepts untrusted input passed directly to LLM
          File: src/pipeline.py:42
          OWASP: LLM01 · EU AI Act: Article 15

HIGH      missing_human_oversight
          Destructive tool call without human approval gate
          File: src/tools.py:28
          OWASP: LLM08 · EU AI Act: Article 14
```

### Output formats

```bash
# SARIF output for GitHub Security tab
inkog -path . -output sarif > results.sarif

# JSON for CI/CD pipelines
inkog -path . -output json

# HTML report
inkog -path . -output html > report.html
```

### CI/CD with GitHub Actions

```yaml
- uses: inkog-io/inkog@v1
  with:
    path: .
    policy: balanced
```

## What It Detects

Inkog detects vulnerabilities specific to AI agents and Haystack pipelines:

| Category | Examples |
|----------|----------|
| Injection | Prompt injection via tainted tool inputs, SQL injection through LLM-generated queries |
| Resource exhaustion | Infinite loops in agent pipelines, token bombing, unbounded context accumulation |
| Missing controls | No human oversight on destructive actions, missing rate limits, absent authorization checks |
| Data safety | Hardcoded credentials, sensitive data in logs, unsafe environment variable access |

Findings are mapped to OWASP LLM Top 10, EU AI Act (Articles 14, 15), and NIST AI RMF.

## License

Apache 2.0
