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
integration ships the following token sources, and you can implement your own:

- **`OAuthRefreshTokenSource`**: runs the RFC 6749 refresh-token grant for a single fixed identity, caching the
  access token in process until shortly before it expires. If the provider rotates the refresh token, the new value
  is surfaced through an optional `on_rotate` callback so you can persist it.
- **`OAuthClientCredentialsSource`**: runs the RFC 6749 client-credentials grant, so the token belongs to the client
  application itself rather than to a user. One token per instance, cached until shortly before it expires.
- **`OAuthTokenExchangeSource`**: exchanges a per-request subject token (an incoming user assertion) for a
  downstream token via RFC 8693 token exchange (and, through configuration, Microsoft's on-behalf-of flow). It is
  multi-user and stateless, so it suits multi-replica deployments. Tokens are cached per subject token (bounded,
  LRU).
- **`EntraAgentOBOTokenSource`**: a preconfigured source for the
  [Microsoft Entra Agent ID on-behalf-of flow](https://learn.microsoft.com/en-us/entra/agent-id/agent-on-behalf-of-oauth-flow),
  which lets an agent call tools as the signed-in user under the agent's own identity.
- **`OAuthStaticTokenSource`**: returns a configured long-lived, non-expiring token as-is, for providers such as
  Slack or Notion where no refresh flow is needed.

`OAuthClientCredentialsSource` and `OAuthTokenExchangeSource` authenticate the client with a `client_secret` or with
a client assertion (RFC 7523) taken from a `client_assertion_source`. For certificate or key-pair credentials,
**`OAuthPrivateKeyJWTSource`** signs that assertion with a private key.

Both synchronous (`run`) and asynchronous (`run_async`) execution are supported.

## Installation

```bash
pip install oauth-haystack
```

To authenticate with a certificate or private key (`OAuthPrivateKeyJWTSource`, or `EntraAgentOBOTokenSource` with a
certificate), install the `jwt` extra:

```bash
pip install "oauth-haystack[jwt]"
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

### Resolve a token for the application itself

Use `OAuthClientCredentialsSource` when a service calls an API with its own identity rather than a user's. Like the
refresh grant, the resolver takes no run input.

```python
from haystack.utils import Secret
from haystack_integrations.components.connectors.oauth import OAuthTokenResolver
from haystack_integrations.utils.oauth import OAuthClientCredentialsSource

resolver = OAuthTokenResolver(
    token_source=OAuthClientCredentialsSource(
        token_url="https://idp.example.com/oauth2/token",
        client_id="my-service",
        client_secret=Secret.from_env_var("OAUTH_CLIENT_SECRET"),
        scopes=["api.read"],
    ),
)

access_token = resolver.run()["access_token"]
```

### Authenticate with a certificate instead of a client secret

Pass an `OAuthPrivateKeyJWTSource` as the `client_assertion_source` of `OAuthClientCredentialsSource` or
`OAuthTokenExchangeSource`. It signs a fresh, short-lived JWT for every request to the token endpoint. The private
key must be an unencrypted PEM key. Set `certificate` for providers that identify the key by its certificate
thumbprint. This requires the `jwt` extra.

```python
from haystack.utils import Secret
from haystack_integrations.utils.oauth import OAuthClientCredentialsSource, OAuthPrivateKeyJWTSource

token_url = "https://idp.example.com/oauth2/token"
source = OAuthClientCredentialsSource(
    token_url=token_url,
    client_id="my-service",
    client_assertion_source=OAuthPrivateKeyJWTSource(
        client_id="my-service",
        audience=token_url,
        private_key=Secret.from_env_var("OAUTH_PRIVATE_KEY"),
        certificate=Secret.from_env_var("OAUTH_CERTIFICATE"),  # optional
    ),
    scopes=["api.read"],
)
```

### Act on behalf of a user with a Microsoft Entra Agent ID

`EntraAgentOBOTokenSource` implements the
[agent on-behalf-of flow](https://learn.microsoft.com/en-us/entra/agent-id/agent-on-behalf-of-oauth-flow) for agent
identities created from an agent identity blueprint. It takes the signed-in user's token as the per-request
`subject_token` and makes up to two requests to the tenant's token endpoint: the blueprint first obtains an
intermediate token for the agent identity (cached until shortly before it expires), and the agent identity then
exchanges it together with the user's token for an access token to the requested resource (cached per user).

Configure exactly one credential for the blueprint: `client_secret`, `certificate` with `private_key` (requires the
`jwt` extra), or a custom `client_assertion_source`, such as a managed identity registered as a federated identity
credential of the blueprint.

```python
from haystack.utils import Secret
from haystack_integrations.components.connectors.oauth import OAuthTokenResolver
from haystack_integrations.utils.oauth import EntraAgentOBOTokenSource

resolver = OAuthTokenResolver(
    token_source=EntraAgentOBOTokenSource(
        tenant_id="<tenant-id>",
        blueprint_client_id="<blueprint-client-id>",
        agent_identity_client_id="<agent-identity-client-id>",
        scopes=["https://graph.microsoft.com/.default"],
        client_secret=Secret.from_env_var("ENTRA_BLUEPRINT_CLIENT_SECRET"),
        # Or authenticate the blueprint with a certificate:
        # certificate=Secret.from_env_var("ENTRA_BLUEPRINT_CERTIFICATE"),
        # private_key=Secret.from_env_var("ENTRA_BLUEPRINT_PRIVATE_KEY"),
    ),
)

# `user_token` is the signed-in user's access token for the blueprint, injected by your application per request.
access_token = resolver.run(subject_token=user_token)["access_token"]
```

Keep in mind what Microsoft Entra expects:

- The user's token must be issued for the blueprint (its `aud` claim is the blueprint's client ID). A token for
  another resource, such as Microsoft Graph, is rejected with `AADSTS50013`.
- An administrator must grant the agent identity the requested delegated permissions, either directly or as
  inheritable permissions on the blueprint. Otherwise the exchange fails with `AADSTS82014`.
- An access token is valid for a single resource, so use one resolver per downstream service.
- For sovereign clouds, set `authority` and `token_exchange_audience`.

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
