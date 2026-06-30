---
layout: integration
name: Microsoft SharePoint
description: Search and fetch content from Microsoft SharePoint and OneDrive via the Microsoft Graph API.
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: haystack_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/microsoft-sharepoint-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/microsoft_sharepoint
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/microsoft-sharepoint.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Authentication](#authentication)
- [Usage](#usage)
- [License](#license)

## Overview

This integration brings content from [Microsoft SharePoint](https://www.microsoft.com/microsoft-365/sharepoint/collaboration)
and OneDrive into your Haystack pipelines through the [Microsoft Graph API](https://learn.microsoft.com/en-us/graph/).
It ships two components:

- **`MSSharePointRetriever`** — searches SharePoint and OneDrive via the Microsoft Search (Graph) API and returns
  one Haystack `Document` per hit. Each document's `content` is the search snippet and its `meta` carries the
  resource metadata (`file_name`, `web_url`, `entity_type`, timestamps, author info, `mime_type`, ...) plus the
  SharePoint identifiers a downstream fetcher needs. It does **not** download the underlying files.
- **`MSSharePointFetcher`** — downloads the full content of SharePoint and OneDrive items and returns them as
  `ByteStream`s, ready for a downstream converter. Files (`driveItem`) come back as their raw bytes, list items as
  JSON, and SharePoint pages (`sitePage`) as HTML. Feed it the retriever's `documents` or a list of `web_url`s.

The two components are designed to work together — and with the [OAuth integration](https://haystack.deepset.ai/integrations/oauth)
for authentication — but each can be used on its own.

## Installation

```bash
pip install microsoft-sharepoint-haystack
```

## Authentication

Both components take a per-user `access_token` as a **run input**: a delegated Microsoft Graph bearer token for the
user whose content is searched or fetched. The Microsoft Search API supports delegated permissions only. The token
must carry the relevant delegated scopes, for example `Files.Read.All` for files and `Sites.Read.All` for
site/list scoping and SharePoint pages.

You typically obtain this token from an upstream `OAuthTokenResolver` (provided by the
[OAuth integration](https://haystack.deepset.ai/integrations/oauth)) and wire it into the components' `access_token`
input. In the examples below the token is passed directly as a string for brevity.

## Usage

### Search SharePoint and OneDrive

```python
from haystack_integrations.components.retrievers.microsoft_sharepoint import MSSharePointRetriever

retriever = MSSharePointRetriever(top_k=5)

# `access_token` is a per-user delegated Microsoft Graph bearer token.
result = retriever.run(query="quarterly roadmap", access_token="my-delegated-graph-token")

for document in result["documents"]:
    print(document.meta["file_name"], "->", document.meta["web_url"])
```

You can scope or filter results with [Keyword Query Language (KQL)](https://learn.microsoft.com/en-us/sharepoint/dev/general-development/keyword-query-language-kql-syntax-reference)
operators directly in the query, for example `quarterly roadmap filetype:docx` or
`path:"https://contoso.sharepoint.com/sites/Team"`.

### Fetch full content

The retriever only returns snippets and metadata. Pass its `documents` (or raw `web_url` strings) to the fetcher to
download the full content as `ByteStream`s:

```python
from haystack_integrations.components.fetchers.microsoft_sharepoint import MSSharePointFetcher

fetcher = MSSharePointFetcher()

result = fetcher.run(
    access_token="my-delegated-graph-token",
    targets=["https://contoso.sharepoint.com/sites/contoso-team/contoso-designs.docx"],
)
streams = result["streams"]
```

Each `ByteStream`'s `meta` carries `url`, `file_name`, `content_type`, and a normalized `entity_type`
(`driveItem`, `listItem`, or `sitePage`), so you can route the streams to the right converter — for example a
`FileTypeRouter` in front of `PyPDFToDocument`, `DOCXToDocument`, or `HTMLToDocument`.

### End-to-end pipeline

The components shine when combined: resolve a token once with the OAuth integration, search with the retriever,
and download the matching items with the fetcher.

```python
from haystack import Pipeline
from haystack.utils import Secret

from haystack_integrations.components.connectors.oauth import OAuthTokenResolver
from haystack_integrations.utils.oauth import OAuthRefreshTokenSource
from haystack_integrations.components.retrievers.microsoft_sharepoint import MSSharePointRetriever
from haystack_integrations.components.fetchers.microsoft_sharepoint import MSSharePointFetcher

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
pipe.add_component("retriever", MSSharePointRetriever(top_k=5))
pipe.add_component("fetcher", MSSharePointFetcher())

# Feed the resolved token into both components and the retrieved hits into the fetcher.
pipe.connect("oauth.access_token", "retriever.access_token")
pipe.connect("oauth.access_token", "fetcher.access_token")
pipe.connect("retriever.documents", "fetcher.targets")

result = pipe.run({"retriever": {"query": "quarterly roadmap"}})
streams = result["fetcher"]["streams"]
```

From here, connect the fetcher's `streams` to a `FileTypeRouter` and the appropriate converters to turn the raw
content into Haystack `Document`s for indexing or RAG.

## License

`microsoft-sharepoint-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
