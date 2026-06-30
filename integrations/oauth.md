---
layout: integration
name: OAuth
description: Resolve OAuth 2.0 access tokens at pipeline runtime to authenticate downstream Haystack components.
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: haystack_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/oauth-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/oauth
type: Custom Component
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/oauth.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

This integration provides the `OAuthTokenResolver`, a component that resolves an [OAuth 2.0](https://oauth.net/2/)
access token at pipeline runtime and emits it on its `access_token` output socket. A downstream component (for
example a SharePoint or Google Drive retriever) consumes the token through a normal pipeline connection and never
needs to know how it was obtained.

The resolver is a thin wrapper over a pluggable **token source** that decides *where* the token comes from. The
integration ships three token sources, and you can implement your own:

- **`OAuthRefreshTokenSource`** — runs the RFC 6749 refresh-token grant for a single fixed identity, caching the
  access token in process until shortly before it expires. If the provider rotates the refresh token, the new value
  is surfaced through an optional `on_rotate` callback so you can persist it.
- **`OAuthTokenExchangeSource`** — exchanges a per-request subject token (an incoming user assertion) for a
  downstream token via RFC 8693 token exchange (and, through configuration, Microsoft's on-behalf-of flow). It is
  multi-user and stateless, so it suits multi-replica deployments. Tokens are cached per subject token (bounded,
  LRU).
- **`OAuthStaticTokenSource`** — returns a configured long-lived, non-expiring token as-is, for providers such as
  Slack or Notion where no refresh flow is needed.

Both synchronous (`run`) and asynchronous (`run_async`) execution are supported.

## Installation

```bash
pip install oauth-haystack
```

## Usage

### Resolve a token from a refresh grant

Use `OAuthRefreshTokenSource` for a single fixed identity backed by a refresh token. The resolver takes no run
input and acts as a source node.

```python
from haystack.utils import Secret
from haystack_integrations.components.connectors.oauth import OAuthTokenResolver
from haystack_integrations.utils.oauth import OAuthRefreshTokenSource

resolver = OAuthTokenResolver(
    token_source=OAuthRefreshTokenSource(
        token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
        client_id="aaa-bbb-ccc",
        refresh_token=Secret.from_env_var("MS_REFRESH_TOKEN"),
        scopes=["https://graph.microsoft.com/Files.Read.All", "offline_access"],
    ),
)

access_token = resolver.run()["access_token"]
```

### Use it in a pipeline

Connect the resolver's `access_token` output to any downstream component that authenticates with a bearer token.
The resolver refreshes and caches the token transparently on every run.

```python
from haystack import Pipeline
from haystack_integrations.components.connectors.oauth import OAuthTokenResolver
from haystack_integrations.utils.oauth import OAuthRefreshTokenSource
from haystack.utils import Secret

pipe = Pipeline()
pipe.add_component(
    "oauth",
    OAuthTokenResolver(
        token_source=OAuthRefreshTokenSource(
            token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
            client_id="aaa-bbb-ccc",
            refresh_token=Secret.from_env_var("MS_REFRESH_TOKEN"),
            scopes=["https://graph.microsoft.com/Files.Read.All", "offline_access"],
        ),
    ),
)
# pipe.add_component("retriever", SomeRetriever(...))  # any component with an access_token input

# Feed the resolved token into the downstream component.
# pipe.connect("oauth.access_token", "retriever.access_token")
```

### Exchange a per-user token (multi-user)

Use `OAuthTokenExchangeSource` when each request carries its own user assertion. Because the source sets
`requires_subject_token = True`, the resolver declares a **mandatory** `subject_token` run input that the
application injects per request.

```python
from haystack.utils import Secret
from haystack_integrations.components.connectors.oauth import OAuthTokenResolver
from haystack_integrations.utils.oauth import OAuthTokenExchangeSource

resolver = OAuthTokenResolver(
    token_source=OAuthTokenExchangeSource(
        token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
        client_id="aaa-bbb-ccc",
        client_secret=Secret.from_env_var("MS_CLIENT_SECRET"),
        # Microsoft on-behalf-of flow
        grant_type="urn:ietf:params:oauth:grant-type:jwt-bearer",
        subject_token_param="assertion",
        scopes=["https://graph.microsoft.com/Files.Read.All"],
        extra_token_params={"requested_token_use": "on_behalf_of"},
    ),
)

# `subject_token` is the incoming user assertion, injected by your application per request.
access_token = resolver.run(subject_token="<incoming-user-assertion>")["access_token"]
```

### Use a static long-lived token

For providers that issue non-expiring tokens, `OAuthStaticTokenSource` returns the configured token as-is.

```python
from haystack.utils import Secret
from haystack_integrations.components.connectors.oauth import OAuthTokenResolver
from haystack_integrations.utils.oauth import OAuthStaticTokenSource

resolver = OAuthTokenResolver(
    token_source=OAuthStaticTokenSource(token=Secret.from_env_var("SLACK_TOKEN")),
)

access_token = resolver.run()["access_token"]
```

## License

`oauth-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
