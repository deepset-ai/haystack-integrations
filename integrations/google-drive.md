---
layout: integration
name: Google Drive
description: Search and fetch files from Google Drive via the Drive API.
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: haystack_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/google-drive-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/google_drive
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/google-drive.png
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

This integration brings files from [Google Drive](https://www.google.com/drive/) into your Haystack pipelines
through the [Google Drive API v3](https://developers.google.com/workspace/drive/api/guides/about-sdk). It ships two
components:

- **`GoogleDriveRetriever`** — runs a full-text search over the user's Drive (and optionally shared drives) via
  the `files.list` endpoint and returns one Haystack `Document` per matching file. Each document carries resource
  metadata (`file_name`, `file_id`, `web_url`, `mime_type`, `file_extension`, author, timestamps). By default the
  `content` is the file `description` or `name`; set `include_content=True` to export native Google
  Docs/Sheets/Slides to text and use that as the content. Binary files (PDF, DOCX, ...) are never downloaded.
- **`GoogleDriveFetcher`** — downloads the full content of Drive files and returns them as `ByteStream`s, ready for
  a downstream converter. Binary files are downloaded as-is, native Google Docs/Sheets/Slides are exported (by
  default to DOCX/XLSX/PPTX), and folders or non-downloadable Google types are skipped. Feed it the retriever's
  `documents` or a list of file ids / Drive URLs.

The two components are designed to work together — and with the [OAuth integration](https://haystack.deepset.ai/integrations/oauth)
for authentication — but each can be used on its own.

## Installation

```bash
pip install google-drive-haystack
```

## Authentication

Both components take a per-user `access_token` as a **run input**: a delegated Google OAuth bearer token for the
user whose Drive is searched or fetched. The token must carry a scope that allows reading file content, for example
`https://www.googleapis.com/auth/drive.readonly`. The metadata-only `drive.metadata.readonly` scope cannot search
file content or export documents.

You typically obtain this token from an upstream `OAuthTokenResolver` (provided by the
[OAuth integration](https://haystack.deepset.ai/integrations/oauth)) and wire it into the components' `access_token`
input. In the standalone examples below the token is passed directly as a string for brevity.

## Usage

### Search Google Drive

```python
from haystack_integrations.components.retrievers.google_drive import GoogleDriveRetriever

retriever = GoogleDriveRetriever(top_k=5)

# `access_token` is a per-user delegated Google OAuth bearer token.
result = retriever.run(query="quarterly roadmap", access_token="my-delegated-google-token")

for document in result["documents"]:
    print(document.meta["file_name"], "->", document.meta["web_url"])
```

Pass `include_content=True` to export native Google Docs/Sheets/Slides to text, `include_shared_drives=True` to span
shared drives, or a `query_filter` (such as `"'<folderId>' in parents"`) to scope the search.

### Fetch full content

The retriever returns only metadata (and optionally exported text). Pass its `documents` (or raw file ids / Drive
URLs) to the fetcher to download the full content as `ByteStream`s:

```python
from haystack_integrations.components.fetchers.google_drive import GoogleDriveFetcher

fetcher = GoogleDriveFetcher()

result = fetcher.run(
    access_token="my-delegated-google-token",
    targets=["https://drive.google.com/file/d/1AbCdEfGhIjKlMnOpQrStUvWxYz/view"],
)
streams = result["streams"]
```

Each `ByteStream`'s `meta` carries `file_id`, `web_url`, `file_name`, and `content_type`, so you can route the
streams to the right converter — for example a `FileTypeRouter` in front of `PyPDFToDocument`, `DOCXToDocument`,
`XLSXToDocument`, or `PPTXToDocument`.

### End-to-end pipeline

The components shine when combined: resolve a token once with the OAuth integration, search with the retriever, and
download the matching files with the fetcher.

```python
from haystack import Pipeline
from haystack.utils import Secret

from haystack_integrations.components.connectors.oauth import OAuthTokenResolver
from haystack_integrations.utils.oauth import OAuthRefreshTokenSource
from haystack_integrations.components.retrievers.google_drive import GoogleDriveRetriever
from haystack_integrations.components.fetchers.google_drive import GoogleDriveFetcher

pipe = Pipeline()
pipe.add_component(
    "oauth",
    OAuthTokenResolver(
        token_source=OAuthRefreshTokenSource(
            token_url="https://oauth2.googleapis.com/token",
            client_id="aaa-bbb-ccc",
            refresh_token=Secret.from_env_var("GOOGLE_REFRESH_TOKEN"),
            scopes=["https://www.googleapis.com/auth/drive.readonly"],
        ),
    ),
)
pipe.add_component("retriever", GoogleDriveRetriever(top_k=5))
pipe.add_component("fetcher", GoogleDriveFetcher())

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

`google-drive-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
