---
layout: integration
name: CareJobs.Now
description: Search open US healthcare jobs and look up posted pay, employers, and job-market numbers from Haystack pipelines and Agents, with no API key.
authors:
    - name: CareJobs.Now
      socials:
        github: yumaheymans
pypi: https://pypi.org/project/carejobs-haystack
repo: https://github.com/yumaheymans/carejobs-haystack
type: Tool Integration
report_issue: https://github.com/yumaheymans/carejobs-haystack/issues
logo: /logos/carejobs.png
version: Haystack 3.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Search jobs and get Documents](#search-jobs-and-get-documents)
  - [Use the jobs in a pipeline](#use-the-jobs-in-a-pipeline)
  - [Look up pay, the job market, a state, or an employer](#look-up-pay-the-job-market-a-state-or-an-employer)
  - [Give an Agent the tools](#give-an-agent-the-tools)
- [License](#license)

## Overview

[CareJobs.Now](https://carejobs.now) is a free US healthcare job board. It reads the open jobs of more than 2,000 hospitals, health systems, clinic groups, and care companies: nurses, CNAs, doctors, NPs and PAs, therapists, imaging and lab techs, pharmacy, caregivers, front office, and more.

The community-maintained `carejobs-haystack` package gives Haystack pipelines and Agents live access to those jobs, their posted pay, the employers, and the job-market numbers through the public CareJobs.Now remote MCP endpoint. **No API key or account is needed.** Every job links to its page on CareJobs.Now, where the person applies.

The package ships three building blocks, each with synchronous and asynchronous calls:

- `CareJobsJobSearch` searches open jobs and returns one `Document` per job. The job is the `content`, and its fields (`title`, `employer`, `kind`, `pay`, `schedule`, `facility`, `location`, `listed`, `url`, `employer_page`) are the `meta`.
- `CareJobsLookup` calls one CareJobs.Now tool and returns its readable `text` and structured `data`: the pay open jobs post, the job market, one state's jobs, the list of employers, or one employer's profile.
- `CareJobsToolset` is the six CareJobs.Now tools (`search_healthcare_jobs`, `get_healthcare_pay`, `get_healthcare_job_market`, `get_healthcare_jobs_by_state`, `list_healthcare_employers`, and `get_healthcare_employer`) as Haystack `Tool`s for an `Agent` or a chat generator.

Pay is what employers post, measured from the hourly rates open jobs state, before shift differentials and bonuses. Results cover US jobs only.

## Installation

```bash
pip install carejobs-haystack
```

The package needs Python 3.11 or later and `haystack-ai` 3.0 or later.

## Usage

### Search jobs and get Documents

```python
from haystack_integrations.components.retrievers.carejobs import CareJobsJobSearch

search = CareJobsJobSearch(kind="nurses", state="TX", top_k=3)
result = search.run(query="ICU")

print(result["total"])  # how many open jobs match
for document in result["documents"]:
    print(document.meta["title"], "|", document.meta["employer"], "|", document.meta["url"])
```

`run()` and `run_async()` take `query`, `kind`, `employer`, `state`, `remote`, `min_hourly_usd`, `sort`, and `top_k`. Anything you leave out uses the value set at initialization. `kind` is one of `nurses`, `nurse-practitioners`, `physicians`, `nursing-assistants`, `caregivers`, `therapy-rehab`, `mental-health`, `pharmacy`, `imaging`, `lab`, `surgical-techs`, `emts-paramedics`, `medical-assistants`, `dental`, `admin`, `allied-health`, or `ai-training`. `state` is a two-letter code (`TX`) or a name (`Texas`). `employer` is a slug such as `kaiser-permanente`, or a name.

The first request after a quiet period can take up to about 25 seconds while the service wakes. The default timeout is 30 seconds. To wait longer, pass `timeout=60`.

### Use the jobs in a pipeline

```python
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack_integrations.components.retrievers.carejobs import CareJobsJobSearch

pipeline = Pipeline()
pipeline.add_component("jobs", CareJobsJobSearch(kind="nursing-assistants", state="OH", top_k=3))
pipeline.add_component(
    "prompt",
    PromptBuilder(
        template="""Open jobs:
{% for doc in documents %}{{ doc.content }}

{% endfor %}
Summarize the best paying job for {{ question }}""",
        required_variables=["documents", "question"],
    ),
)
pipeline.connect("jobs.documents", "prompt.documents")

result = pipeline.run({"jobs": {"query": "night"}, "prompt": {"question": "a night-shift CNA"}})
print(result["prompt"]["prompt"])
```

Connect `prompt` to a chat generator to get an answer.

### Look up pay, the job market, a state, or an employer

```python
from haystack_integrations.components.retrievers.carejobs import CareJobsLookup

pay = CareJobsLookup(tool_name="get_healthcare_pay")
result = pay.run(arguments={"kind": "nursing-assistants"})
print(result["text"])  # the readable summary
print(result["data"])  # the structured answer (a dict)

employer = CareJobsLookup(tool_name="get_healthcare_employer")
print(employer.run(arguments={"employer": "kaiser-permanente"})["text"])
```

### Give an Agent the tools

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.tools.carejobs import CareJobsToolset

agent = Agent(chat_generator=OpenAIChatGenerator(), tools=CareJobsToolset())

result = agent.run(
    messages=[
        ChatMessage.from_user(
            "Find night-shift ICU nursing jobs in Texas that pay at least $45 an hour, "
            "and tell me which employers post the most for nurses."
        )
    ]
)
print(result["last_message"].text)
```

Set `OPENAI_API_KEY` for this example, or use any other chat generator that supports tools. If CareJobs.Now rejects a call (for example an unknown employer), the `Agent` hands the service's message back to the model, which can correct the call.

Components and the toolset serialize with `to_dict()` and `from_dict()`, so pipelines and Agents that use them save and load with `dumps()` and `loads()`.

## License

`carejobs-haystack` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
