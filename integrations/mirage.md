---
layout: integration
name: Mirage
description: Give a Haystack Agent a bash shell over Mirage's unified virtual filesystem, mounting S3, Google Drive, Postgres and 50+ other backends as one filesystem
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: haystack_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/mirage-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/mirage
type: Tool Integration
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/mirage.svg
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Security model](#security-model)
- [License](#license)

## Overview

[Mirage](https://github.com/strukto-ai/mirage) is a unified virtual filesystem for AI agents: it
mounts heterogeneous backends — object storage (S3, GCS, R2), databases (Postgres, MongoDB, Redis),
and SaaS apps (Google Drive, Gmail, Slack, GitHub, Notion) — as a single filesystem, so every service
speaks the same familiar Unix semantics. An agent can `ls`, `cat`, `grep` and pipe across mounts
exactly as it would on local disk, without learning a new API for each backend.

The `mirage-haystack` integration wraps Mirage as a Haystack
[`Tool`](https://docs.haystack.deepset.ai/docs/tool) that an
[`Agent`](https://docs.haystack.deepset.ai/docs/agent) can invoke to run bash commands across the
mounted filesystem. Instead of pre-loading data into a pipeline, you hand the agent one well-described
tool and let it explore the mounts itself to answer a question.

## Installation

```bash
pip install mirage-haystack
```

## Usage

### Components

This integration introduces the following:

- `MirageMount`: A declarative, serializable description of a single backend mounted into the
  workspace — its mount `path` (e.g. `/s3`), its Mirage `resource` name (e.g. `"s3"`, `"gdrive"`,
  `"postgres"`), its `config`, and whether it is `read_only`. Credentials can be passed as Haystack
  `Secret`s. Call `MirageMount.available_resources()` to list every backend name you can mount.
- `MirageWorkspace`: Holds a list of `MirageMount`s and lazily builds the live `mirage.Workspace` on
  first use. It serializes cleanly (resolving `Secret`s only at build time) and can also be run
  directly via `run()` / `run_async()`.
- `MirageShellTool`: A Haystack `Tool` that exposes the workspace's `execute` surface to an `Agent`
  through a single `command` parameter. Output is normalized to text and truncated before it reaches
  the model. It carries the security guards (`allowed_commands`, `denied_paths`) described below.

### Use with a Haystack Agent

Mount a directory (or any Mirage backend) read-only and give an `Agent` a `MirageShellTool` it can
drive with ordinary bash — the agent explores the files itself to answer:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from haystack_integrations.tools.mirage import MirageMount, MirageShellTool, MirageWorkspace

workspace = MirageWorkspace(
    mounts=[
        MirageMount(path="/data", resource="ram"),
        MirageMount(path="/s3", resource="s3", config={"bucket": "my-bucket"}, read_only=True),
    ]
)
tool = MirageShellTool(workspace, allowed_commands=["ls", "cat", "grep", "head", "wc", "cp"])

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=[tool],
    system_prompt=(
        "A virtual filesystem is available through the `mirage_shell` tool. Use bash commands "
        "(ls, cat, grep, wc, ...) to inspect the mounts before answering. Base your answer only "
        "on what the files actually show."
    ),
)
agent.warm_up()

result = agent.run(
    messages=[ChatMessage.from_user("How many lines in /s3/log.txt mention 'alert'?")]
)
print(result["messages"][-1].text)

tool.close()
```

Every backend is mounted the same way — swap the `MirageMount` for the one you need. Values that are
credentials should be wrapped in a `Secret`:

```python
from haystack.utils import Secret
from haystack_integrations.tools.mirage import MirageMount

MirageMount(path="/data", resource="ram")                                   # in-memory scratch
MirageMount(path="/local", resource="disk", config={"root": "/srv/data"})   # local disk
MirageMount(path="/s3", resource="s3", config={"bucket": "my-bucket"}, read_only=True)
MirageMount(
    path="/drive",
    resource="gdrive",
    config={"client_id": "...", "refresh_token": Secret.from_env_var("GDRIVE_REFRESH_TOKEN")},
    read_only=True,
)
```

### Run the workspace directly

You don't need an `Agent` to use a workspace — call `run()` to execute a command yourself. This is
handy for testing mounts or composing across backends in plain Python:

```python
from haystack_integrations.tools.mirage import MirageMount, MirageWorkspace

ws = MirageWorkspace(
    mounts=[
        MirageMount(path="/data", resource="ram"),
        MirageMount(path="/s3", resource="s3", config={"bucket": "my-bucket"}, read_only=True),
    ]
)
print(ws.run("grep -r alert /s3/logs | wc -l"))
ws.close()
```

## Security model

Mirage never shells out to the host: every command runs inside Mirage's own virtual-filesystem
interpreter. Three controls shape what an Agent can do:

- **Per-mount read-only mode** (`MirageMount(..., read_only=True)`) is the authoritative write
  boundary. Mirage refuses any write to a read-only mount regardless of the command used, so this
  is how you prevent modification or deletion. Mount anything the Agent should not change as read-only.
- **The command allowlist** (`allowed_commands`) restricts *which* commands may run. It is enforced
  against every command Mirage would execute, including commands nested inside `$(...)`, backticks,
  `<(...)` and subshells, so `ls "$(rm x)"` is rejected unless `rm` is also allowed. Treat it as a
  best-effort filter to steer the Agent, not a sandbox: allowing a command that itself runs other
  commands (`eval`, `bash`, `sh`, `source`, `xargs`, `timeout`) effectively allows anything, so do not
  list those for untrusted/hosted use.
- **`denied_paths`** rejects any command whose text references one of the given path substrings.

## License

`mirage-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
