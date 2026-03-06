---
layout: integration
name: Open WebUI
description: Use Open WebUI as a chat frontend for your Haystack apps through Hayhooks
authors:
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/hayhooks/
repo: https://github.com/deepset-ai/hayhooks
type: UI
report_issue: https://github.com/deepset-ai/hayhooks/issues
logo: /logos/openwebui.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Open WebUI](https://openwebui.com/) is an open-source chat UI for LLM apps. By exposing your Haystack pipelines and agents through [Hayhooks](https://github.com/deepset-ai/hayhooks) as OpenAI-compatible endpoints, you can use Open WebUI as the frontend: run Hayhooks and Open WebUI (separately or via Docker Compose), then connect Open WebUI to Hayhooks in Settings. You get streaming, optional [status and notification events](https://deepset-ai.github.io/hayhooks/features/openwebui-integration#open-webui-events), and optional [OpenAPI tool server](https://deepset-ai.github.io/hayhooks/features/openwebui-integration#openapi-tool-server) integration.

For full details, see the [Hayhooks Open WebUI integration guide](https://deepset-ai.github.io/hayhooks/features/openwebui-integration).

## Installation

Install Hayhooks:

```bash
pip install hayhooks
```

Install and run Open WebUI separately, e.g. with Docker:

```bash
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -e WEBUI_AUTH=False -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:main
```

For a pre-wired setup, use the [Hayhooks + Open WebUI Docker Compose](https://github.com/deepset-ai/hayhooks-open-webui-docker-compose) (see [Quick Start with Docker Compose](https://deepset-ai.github.io/hayhooks/getting-started/quick-start-docker/)).

## Usage

### Connect Open WebUI to Hayhooks

1. Start Hayhooks with your pipelines:

   ```bash
   hayhooks run --pipelines-dir ./pipelines
   ```

2. In Open WebUI go to **Settings → Connections** and add a connection:
   - **API Base URL**: `http://localhost:1416` (or `http://hayhooks:1416/v1` when using Docker Compose)
   - **API Key**: any value (Hayhooks does not require auth)

3. In a new chat, select your deployed pipeline as the model.

Pipeline wrappers must support chat completion (e.g. implement `run_chat_completion` or `run_chat_completion_async`). See [OpenAI compatibility](https://deepset-ai.github.io/hayhooks/features/openai-compatibility) and the [pipeline examples](https://deepset-ai.github.io/hayhooks/examples/overview/) for implementation details.

### Optional: Open WebUI events

For status updates, notifications, and tool-call feedback in the UI, use helpers from `hayhooks.open_webui` in your pipeline and stream `OpenWebUIEvent` objects. See [Open WebUI Events](https://deepset-ai.github.io/hayhooks/examples/openwebui-events/) and the [open_webui_agent_events](https://github.com/deepset-ai/hayhooks/tree/main/examples/pipeline_wrappers/open_webui_agent_events) and [open_webui_agent_on_tool_calls](https://github.com/deepset-ai/hayhooks/tree/main/examples/pipeline_wrappers/open_webui_agent_on_tool_calls) examples.

## License

`hayhooks` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license. Open WebUI is subject to its [own license](https://github.com/open-webui/open-webui).