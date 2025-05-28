---
layout: integration
name: github
description: Interact with GitHub repositories, issues, and pull requests within Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/github-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/github
type: Tools
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/github.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

The GitHub integration for Haystack provides a set of components and tools to interact with GitHub repositories, issues, and pull requests. It enables you to view repository contents, manage issues, create pull requests, and more within your Haystack agents and pipelines.


Some of the components and tools in this integration require GitHub authentication with a personal access token. 
For example, authentication is required to post a comment on GitHub, fork a repository, or open a pull request. You can create a (fine-graind personal access token)[https://github.com/settings/personal-access-tokens] or a [classic personal access token](https://github.com/settings/tokens) on GitHub and then expose it via an environment variable called `GITHUB_API_KEY`.


## Installation

Install the GitHub integration with pip:

```bash
pip install github-haystack
```

## Usage

This integration comes with several components and tools:

### Components
- `GitHubIssueViewer`: View issues and their details
- `GitHubIssueCommenter`: Add comments to issues
- `GitHubRepoViewer`: View repository contents and metadata
- `GitHubRepoForker`: Fork repositories
- `GitHubFileEditor`: Edit files in repositories
- `GitHubPRCreator`: Create pull requests

### Tools
- `GitHubIssueViewerTool`: View issues
- `GitHubIssueCommenterTool`: Comment on issues
- `GitHubRepoViewerTool`: View repository contents
- `GitHubFileEditorTool`: Edit repository files
- `GitHubPRCreatorTool`: Create pull requests

### Example Usage

```python
from typing import List

from haystack import Pipeline
from haystack.components.agents import Agent
from haystack.components.builders import ChatPromptBuilder
from haystack.dataclasses import ChatMessage, Document
from haystack.tools.from_function import tool

from haystack_integrations.components.connectors.github import GitHubIssueViewer
from haystack_integrations.components.generators.anthropic import AnthropicChatGenerator

from haystack_integrations.prompts.github import SYSTEM_PROMPT

from haystack_integrations.tools.github import GitHubRepoViewerTool
repo_viewer_tool = GitHubRepoViewerTool()

@tool
def create_comment(comment: str) -> str:
    """
    Use this to create a Github comment once you finished your exploration.
    """
    # A mockup tool to showcase how Agent uses tools. You should use `GitHubIssueCommenterTool` instead of this one to write comments on GitHub.
    return comment

chat_generator = AnthropicChatGenerator(model="claude-3-5-sonnet-latest", generation_kwargs={"max_tokens": 8000})

agent = Agent(
    chat_generator=chat_generator,
    system_prompt=SYSTEM_PROMPT,
    tools=[repo_viewer_tool, create_comment],
    exit_conditions=["create_comment"],
    state_schema={"documents": {"type": List[Document]}},
)

issue_template = """
Issue from: {{ url }}
{% for document in documents %}
{% if loop.index == 1 %}
**Title: {{ document.meta.title }}**
{% endif %}
<issue-comment>
{{document.content}}
</issue-comment>
{% endfor %}
    """

issue_builder = ChatPromptBuilder(template=[ChatMessage.from_user(issue_template)], required_variables="*")

issue_fetcher = GitHubIssueViewer()

pipeline = Pipeline()

pipeline.add_component("issue_fetcher", issue_fetcher)
pipeline.add_component("issue_builder", issue_builder)
pipeline.add_component("agent", agent)

pipeline.connect("issue_fetcher.documents", "issue_builder.documents")
pipeline.connect("issue_builder.prompt", "agent.messages")

issue_url = "https://github.com/<owner>/<repo>/issues/1268"

result = pipeline.run({"url": issue_url})
print(result["agent"]["last_message"].tool_call_result.result)
```
