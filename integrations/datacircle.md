---
layout: integration
name: Datacircle
description: Find the best GTM APIs. Our API is free and open, with no key: list every API, see who is best for each and search every plan.
authors:
    - name: Datacircle
      socials:
        github: waynehamadi
        linkedin: https://www.linkedin.com/company/datacircle-org
repo: https://github.com/waynehamadi/datacircle
report_issue: https://github.com/waynehamadi/datacircle/issues
type: Tool Integration
version: Haystack 2.0
toc: true
---

## Overview

Find the best GTM APIs. We benchmark all the GTM APIs and we put the results on [our website](https://datacircle.dev).

Our API is free and open, with no key, at `https://api.datacircle.dev/v1`. Its spec is at `https://api.datacircle.dev/v1/openapi.json`, so a Haystack Agent can call it as any OpenAPI tool.

## Calls

- `GET /apis` lists every API on our sheet.
- `GET /apis/{slug}/best` gives who is best for one API.
- `GET /plans` lists every plan, by API, provider or price.
- `GET /providers/{slug}` gives one provider's ranks.

```bash
curl -s https://api.datacircle.dev/v1/apis
```

## MCP server

Our MCP server is open to anyone, with no key: `https://api.datacircle.dev/mcp`.

## License

Read only, 60 calls a minute from one address. More at [datacircle.dev](https://datacircle.dev).
