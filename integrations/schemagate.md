---
layout: integration
name: schemagate
description: "Save tokens on text-to-SQL: give a Haystack agent only the tables a question needs (about 91% fewer schema tokens on 50+ table databases) and only the ones the caller may read. #1 on the BIRD Mini-Dev leaderboard."
authors:
    - name: Ashish Sinha
      socials:
        github: ashishsinha1602
pypi: https://pypi.org/project/schemagate/
repo: https://github.com/ashishsinha1602/schemagate
type: Tool Integration
report_issue: https://github.com/ashishsinha1602/schemagate/issues
logo: /logos/schemagate.png
version: Haystack 2.0
toc: true
mcp: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [License](#license)

## Overview

**[schemagate](https://github.com/ashishsinha1602/schemagate)** saves tokens on text-to-SQL. Most text-to-SQL setups paste the whole database schema into the prompt, or let the agent browse it table by table. On a database with hundreds of tables that is most of the prompt, on every question. schemagate ranks the tables for each question (keyword and embedding retrieval, foreign-key expansion, join-table recovery) and hands the agent DDL for only the ones it needs.

- **About 91% fewer schema tokens** on databases with 50+ tables (median, Spider 2.0-lite; [BENCHMARKS.md](https://github.com/ashishsinha1602/schemagate/blob/main/BENCHMARKS.md)).
- **Accuracy kept:** #1 on the official [BIRD Mini-Dev leaderboard](https://bird-bench.github.io/) in SQLite, PostgreSQL and MySQL (81.0 / 72.6 / 72.4 execution accuracy), and 74.34 on BIRD's hidden test set, scored by the BIRD team.
- **Per-user scope:** the agent only sees the tables and columns the caller may read (a policy file or the database's own GRANTs). `run_query` refuses writes, multiple statements and any table outside that scope, including inside subqueries.
- **One server for every engine:** PostgreSQL, MySQL, SQLite, SQL Server, Oracle, Snowflake, BigQuery and DuckDB.

schemagate is an MCP server, so this integration uses `mcp-haystack`'s `MCPToolset` to connect it to any Haystack agent over stdio. It is also available as `langchain-schemagate` (listed in LangChain's retriever integrations) and as a LlamaIndex retriever.

## Installation

```bash
pip install mcp-haystack uv
```

`uv` provides `uvx`, which runs the schemagate server in its own environment. Add the driver for your database to the `--from` argument below: `schemagate[mcp,postgres]`, `mysql`, `mssql` or `oracle` (SQLite needs none).

## Usage

The snippet connects to schemagate's bundled `demo` schema (42 tables and views, no credentials needed), selects the schema for a question and runs one query. For your own database, set `SCHEMAGATE_DATABASE_URL` to its SQLAlchemy URL, for example `postgresql+psycopg://readonly_user@host/app`, and use a read-only database user.

```python
from haystack_integrations.tools.mcp import MCPToolset, StdioServerInfo

server_info = StdioServerInfo(
    command="uvx",
    args=["--from", "schemagate[mcp]==1.15.4", "schemagate-mcp"],
    env={"SCHEMAGATE_DATABASE_URL": "demo"},
)
toolset = MCPToolset(
    server_info=server_info,
    tool_names=["select_schema", "run_query"],
    eager_connect=True,
)

select_schema = next(t for t in toolset if t.name == "select_schema")
run_query = next(t for t in toolset if t.name == "run_query")

# Only the tables this question needs, as compact DDL
print(select_schema.invoke(question="How many orders did each customer place?"))

print(run_query.invoke(sql=(
    "SELECT c.id, COUNT(o.id) AS orders FROM main.crm_customer c "
    "JOIN main.sales_order o ON o.id_customer = c.id GROUP BY c.id LIMIT 3"
)))

toolset.close()
```

`select_schema` and `run_query` also take `principal` and `roles`. Pass them to scope what the agent sees to one user: in the demo, the `hr_compensation` table is visible only to the `payroll` role.

## Examples

Connect the toolset to a Haystack `Agent`. The agent selects the schema first, writes one SELECT against that DDL only, and runs it:

```python
from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.anthropic import AnthropicChatGenerator
from haystack_integrations.tools.mcp import MCPToolset, StdioServerInfo
import os

os.environ["ANTHROPIC_API_KEY"] = "YOUR_ANTHROPIC_API_KEY"

toolset = MCPToolset(
    server_info=StdioServerInfo(
        command="uvx",
        args=["--from", "schemagate[mcp]==1.15.4", "schemagate-mcp"],
        env={"SCHEMAGATE_DATABASE_URL": "demo"},
    ),
    tool_names=["select_schema", "run_query", "describe_object"],
    eager_connect=True,
)

agent = Agent(
    chat_generator=AnthropicChatGenerator(model="claude-sonnet-5-5"),
    tools=toolset,
    system_prompt=(
        "Answer questions about the database. First call select_schema with the question. "
        "Write one SELECT using only the tables and columns in its ddl field, then run it "
        "with run_query. If a query is refused as not available to this caller, say so."
    ),
)

result = agent.run(messages=[ChatMessage.from_user("Which five customers placed the most orders?")])
print(result["last_message"].text)
```

## License

schemagate is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license. `mcp-haystack` is also Apache-2.0.
