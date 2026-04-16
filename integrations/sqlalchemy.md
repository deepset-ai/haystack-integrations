---
layout: integration
name: SQLAlchemy
description: Query any SQL database from a Haystack pipeline using SQLAlchemy
authors:
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/sqlalchemy-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/sqlalchemy
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/sqlalchemy.png
version: Haystack 2.0
toc: true
---

**Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Security](#security)
- [License](#license)

## Overview

The SQLAlchemy integration provides a `SQLAlchemyTableRetriever` component that connects to any
[SQLAlchemy](https://www.sqlalchemy.org/)-supported database, executes a SQL query, and returns
results as a Pandas DataFrame and an optional Markdown-formatted table string.

Supported backends include PostgreSQL, MySQL, MariaDB, SQLite, MSSQL, and Oracle — anything
SQLAlchemy supports works out of the box.

This component is designed for Text-to-SQL pipelines where an LLM generates a SQL query and the
retriever fetches the corresponding rows for downstream processing.

## Installation

```bash
pip install sqlalchemy-haystack
```

You also need to install the appropriate database driver for your backend:

| Backend | Driver package |
|---------|----------------|
| PostgreSQL | `psycopg2-binary` or `psycopg[binary]` |
| MySQL / MariaDB | `pymysql` or `mysqlclient` |
| SQLite | built-in (no extra package needed) |
| MSSQL | `pyodbc` |
| Oracle | `cx_oracle` or `oracledb` |

## Usage

### SQLite (in-memory)

```python
from haystack_integrations.components.retrievers.sqlalchemy import SQLAlchemyTableRetriever

retriever = SQLAlchemyTableRetriever(
    drivername="sqlite",
    database=":memory:",
    init_script=[
        "CREATE TABLE products (id INTEGER, name TEXT, price REAL)",
        "INSERT INTO products VALUES (1, 'Widget', 9.99)",
        "INSERT INTO products VALUES (2, 'Gadget', 19.99)",
    ],
)
retriever.warm_up()

result = retriever.run(query="SELECT * FROM products WHERE price < 15")
print(result["dataframe"])
print(result["table"])
```

### PostgreSQL

```python
from haystack.utils import Secret
from haystack_integrations.components.retrievers.sqlalchemy import SQLAlchemyTableRetriever

retriever = SQLAlchemyTableRetriever(
    drivername="postgresql+psycopg2",
    host="localhost",
    port=5432,
    database="mydb",
    username="myuser",
    password=Secret.from_env_var("DB_PASSWORD"),
)
retriever.warm_up()

result = retriever.run(query="SELECT * FROM orders LIMIT 10")
print(result["dataframe"])
```


## Security

This component executes raw SQL queries at runtime. Keep the following in mind:

- **Never pass unsanitised user input** directly as a query — this exposes you to SQL injection.
- **Use a read-only database user.** Even if a malicious query is executed, a read-only user cannot modify or delete data.
- **Restrict database permissions** to the minimum required — specific tables and schemas only, no DDL privileges (`CREATE`, `DROP`, `ALTER`).

## License

`sqlalchemy-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
