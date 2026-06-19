---
layout: integration
name: OpenAPI
description: Connect Haystack pipelines to any REST API described by an OpenAPI specification
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/openapi-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/openapi
type: Connector
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/openapi.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Consider using MCP instead](#consider-using-mcp-instead)
- [Installation](#installation)
- [Usage](#usage)
  - [Components](#components)
  - [Standalone](#standalone)
  - [Pipeline](#pipeline)
- [License](#license)

## Overview

[OpenAPI](https://www.openapis.org/) (formerly Swagger) is a widely used standard for describing REST APIs. The `openapi-haystack` integration lets your Haystack pipelines and LLMs call any OpenAPI-compliant service: you can invoke endpoints directly from a specification, or turn a spec into tool/function definitions that an LLM can call.

> **💡 Consider using MCP instead**
>
> The OpenAPI components are a legacy way to connect Haystack to external APIs. For most use cases, we recommend using the [`MCPTool`](https://docs.haystack.deepset.ai/docs/mcptool) instead: it is the modern, standardized way to give your pipelines and agents access to external tools and services. Reach for the OpenAPI components only when you specifically need to work from an OpenAPI specification.

## Consider using MCP instead

If you are building new pipelines or agents that need to call external tools and services, prefer the [`MCPTool`](https://docs.haystack.deepset.ai/docs/mcptool). It provides a standardized, well-supported way to expose tools to LLMs and integrates natively with Haystack's tooling and agents. The OpenAPI components documented below remain available for cases where you must consume an existing OpenAPI specification directly.

## Installation

Install the `openapi-haystack` package:

```bash
pip install openapi-haystack
```

## Usage

### Components

This integration provides three components:

- [`OpenAPIConnector`](https://docs.haystack.deepset.ai/docs/openapiconnector): directly invokes a REST endpoint described in an OpenAPI specification, by `operation_id` and explicit arguments. It does not require an LLM.
- [`OpenAPIServiceToFunctions`](https://docs.haystack.deepset.ai/docs/openapiservicetofunctions): converts an OpenAPI specification into tool/function definitions suitable for LLM tool calling.
- [`OpenAPIServiceConnector`](https://docs.haystack.deepset.ai/docs/openapiserviceconnector): invokes a service operation based on the tool calls produced by a Chat Generator, returning the response as a `ChatMessage`.

### Standalone

`OpenAPIConnector` calls a REST endpoint directly, without an LLM. The example below queries the keyless [Open-Meteo](https://open-meteo.com/) historical weather API:

```python
import json

from haystack_integrations.components.connectors.openapi import OpenAPIConnector

open_meteo_spec = {
    "openapi": "3.0.0",
    "info": {"title": "Open-Meteo Historical Weather API", "version": "1.0.0"},
    "servers": [{"url": "https://archive-api.open-meteo.com"}],
    "paths": {
        "/v1/archive": {
            "get": {
                "operationId": "get_archive",
                "parameters": [
                    {"name": "latitude", "in": "query", "required": True, "schema": {"type": "number"}},
                    {"name": "longitude", "in": "query", "required": True, "schema": {"type": "number"}},
                    {"name": "start_date", "in": "query", "required": True, "schema": {"type": "string"}},
                    {"name": "end_date", "in": "query", "required": True, "schema": {"type": "string"}},
                    {"name": "daily", "in": "query", "required": False, "schema": {"type": "string"}},
                ],
                "responses": {"200": {"description": "Historical weather data"}},
            }
        }
    },
}

connector = OpenAPIConnector(openapi_spec=json.dumps(open_meteo_spec))

response = connector.run(
    operation_id="get_archive",
    arguments={
        "latitude": 52.52,
        "longitude": 13.41,
        "start_date": "2024-01-01",
        "end_date": "2024-01-07",
        "daily": "temperature_2m_max",
    },
)

print(response["response"]["daily"]["temperature_2m_max"])
```

For services that require authentication, pass the credentials wrapped in a `Secret`:

```python
from haystack.utils import Secret
from haystack_integrations.components.connectors.openapi import OpenAPIConnector

connector = OpenAPIConnector(
    openapi_spec="https://bit.ly/serperdev_openapi",
    credentials=Secret.from_env_var("SERPERDEV_API_KEY"),
)
response = connector.run(operation_id="search", arguments={"q": "Who was Nikola Tesla?"})
```

### Pipeline

`OpenAPIServiceToFunctions` and `OpenAPIServiceConnector` work together to let an LLM decide which operation to call and with which arguments. The pipeline below converts an OpenAPI spec into function definitions, lets an `OpenAIChatGenerator` produce a tool call, invokes the service, and then summarizes the result. It uses the keyless Open-Meteo API, so you only need an `OPENAI_API_KEY`:

```python
import json
from typing import Any

from haystack import Pipeline
from haystack.components.converters import OutputAdapter
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.dataclasses.byte_stream import ByteStream
from haystack_integrations.components.connectors.openapi import OpenAPIServiceConnector
from haystack_integrations.components.converters.openapi import OpenAPIServiceToFunctions

open_meteo_spec = {
    "openapi": "3.0.0",
    "info": {"title": "Open-Meteo Historical Weather API", "version": "1.0.0"},
    "servers": [{"url": "https://archive-api.open-meteo.com"}],
    "paths": {
        "/v1/archive": {
            "get": {
                "operationId": "get_archive",
                "description": "Get historical daily weather data for a location and date range.",
                "parameters": [
                    {"name": "latitude", "in": "query", "required": True,
                     "description": "Latitude of the location", "schema": {"type": "number"}},
                    {"name": "longitude", "in": "query", "required": True,
                     "description": "Longitude of the location", "schema": {"type": "number"}},
                    {"name": "start_date", "in": "query", "required": True,
                     "description": "Start date in YYYY-MM-DD format", "schema": {"type": "string"}},
                    {"name": "end_date", "in": "query", "required": True,
                     "description": "End date in YYYY-MM-DD format", "schema": {"type": "string"}},
                    {"name": "daily", "in": "query", "required": True,
                     "description": "Comma-separated daily variables, e.g. temperature_2m_max",
                     "schema": {"type": "string"}},
                ],
                "responses": {
                    "200": {
                        "description": "Historical weather data",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    }
                },
            }
        }
    },
}


def prepare_fc_params(openai_functions_schema: dict[str, Any]) -> dict[str, Any]:
    return {
        "tools": [{"type": "function", "function": openai_functions_schema}],
        "tool_choice": {"type": "function", "function": {"name": openai_functions_schema["name"]}},
    }


pipe = Pipeline()
pipe.add_component("spec_to_functions", OpenAPIServiceToFunctions())
pipe.add_component("functions_llm", OpenAIChatGenerator(model="gpt-4.1-nano"))
pipe.add_component("openapi_container", OpenAPIServiceConnector())
pipe.add_component(
    "prepare_fc_adapter",
    OutputAdapter("{{functions[0] | prepare_fc}}", dict[str, Any], {"prepare_fc": prepare_fc_params}),
)
pipe.add_component("openapi_spec_adapter", OutputAdapter("{{specs[0]}}", dict[str, Any], unsafe=True))
pipe.add_component(
    "final_prompt_adapter",
    OutputAdapter("{{system_message + service_response}}", list[ChatMessage], unsafe=True),
)
pipe.add_component("llm", OpenAIChatGenerator(model="gpt-4.1-nano"))

pipe.connect("spec_to_functions.functions", "prepare_fc_adapter.functions")
pipe.connect("spec_to_functions.openapi_specs", "openapi_spec_adapter.specs")
pipe.connect("prepare_fc_adapter", "functions_llm.generation_kwargs")
pipe.connect("functions_llm.replies", "openapi_container.messages")
pipe.connect("openapi_spec_adapter", "openapi_container.service_openapi_spec")
pipe.connect("openapi_container.service_response", "final_prompt_adapter.service_response")
pipe.connect("final_prompt_adapter", "llm.messages")

system_prompt = "You are a helpful assistant. Use the provided weather data to answer the user's question."
query = (
    "What was the daily maximum temperature (temperature_2m_max) in Berlin "
    "(latitude 52.52, longitude 13.41) from 2024-01-01 to 2024-01-07?"
)

result = pipe.run(
    data={
        "functions_llm": {
            "messages": [ChatMessage.from_system("Only do tool/function calling"), ChatMessage.from_user(query)]
        },
        "spec_to_functions": {"sources": [ByteStream.from_string(json.dumps(open_meteo_spec))]},
        "final_prompt_adapter": {"system_message": [ChatMessage.from_system(system_prompt)]},
    }
)

print(result["llm"]["replies"][0].text)
```

## License

`openapi-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
