---
layout: integration
name: Snowflake
description: A Snowflake integration that allows table retrieval from a Snowflake database.
authors:
  - name: Mohamed Sriha
    socials:
      github: medsriha
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/snowflake-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/snowflake
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
type: Data Ingestion
logo: /logos/snowflake.png
version: Haystack 2.0
---

[![PyPI - Version](https://img.shields.io/pypi/v/snowflake-haystack.svg)](https://pypi.org/project/snowflake-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/snowflake-haystack.svg)](https://pypi.org/project/snowflake-haystack)
-----

**Table of Contents**

- [Snowflake table retriever for Haystack](#snowfkale-table-retriever-for-haystack)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Examples](#examples)
  - [License](#license)

## Installation
Use `pip` to install Snowflake:

```console
pip install snowflake-haystack
```
## Usage
Once installed, initialize the `SnowflakeTableRetriever` to use it with Haystack:

```python
from haystack_integrations.components.retrievers.snowflake import SnowflakeTableRetriever

# Provide your Snowflake credentials during intialization.
executor = SnowflakeTableRetriever(
    user="<ACCOUNT-USER>",
    account="<ACCOUNT-IDENTIFIER>",
    api_key=Secret.from_env_var("SNOWFLAKE_API_KEY"),
    warehouse="<WAREHOUSE-NAME>",
)
```

Ensure you have `select` access to the tables before querying the database. More details [here](https://docs.snowflake.com/en/user-guide/security-access-control-privileges):
```python
response = executor.run(query="""select * from database_name.schema_name.table_name""")
```
During component initialization, you could provide the schema and database name to avoid needing to provide them in the SQL query:
```python
executor = SnowflakeTableRetriever(
    ...
    schema_name="<SCHEMA-NAME>",
    database ="<DB-NAME>"
)

response = executor.run(query="""select * from table_name""")
```
Snowflake table retriever returns a Pandas dataframe and a Markdown version of the table:
```python

print(response["dataframe"].head(2))  # Pandas dataframe
#   Column 1  Column 2
# 0       Value1 Value2
# 1       Value1 Value2

print(response["table"])  # Markdown
# | Column 1  | Column 2  |
# |:----------|:----------|
# | Value1    | Value2    |
# | Value1    | Value2    |
```

Using `SnowflakeTableRetriever` within a pipeline:

```python
from haystack import Pipeline
from haystack.utils import Secret
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack_integrations.components.retrievers.snowflake import SnowflakeTableRetriever

executor = SnowflakeTableRetriever(
    user="<ACCOUNT-USER>",
    account="<ACCOUNT-IDENTIFIER>",
    api_key=Secret.from_env_var("SNOWFLAKE_API_KEY"),
    warehouse="<WAREHOUSE-NAME>",
)

pipeline = Pipeline()
pipeline.add_component("builder", PromptBuilder(template="Describe this table: {{ table }}"))
pipeline.add_component("snowflake", executor)
pipeline.add_component("llm", OpenAIGenerator(model="gpt-4o"))

pipeline.connect("snowflake.table", "builder.table")
pipeline.connect("builder", "llm")

pipeline.run(data={"query": "select employee, salary from table limit 10;"})
```

## Examples
You can find a code example showing how to use the Snowflake Retriever under the `example/` folder of [this repo](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/snowflake).

## License

`snowflake-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.