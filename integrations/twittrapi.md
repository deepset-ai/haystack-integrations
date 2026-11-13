---
layout: integration
name: TwittrAPI
description: Search X (Twitter) into Documents and give Agents read-only X tools
authors:
    - name: TwittrAPI
      socials:
        github: twittrapi
pypi: https://pypi.org/project/twittrapi-haystack
repo: https://github.com/twittrapi/twittrapi-haystack
report_issue: https://github.com/twittrapi/twittrapi-haystack/issues
type: Search & Extraction
logo: /logos/twittrapi.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [TwittrAPITweetSearch](#twittrapitweetsearch)
- [TwittrAPIToolset](#twittrapitoolset)
- [License](#license)

## Overview

[TwittrAPI](https://www.twittrapi.com) is a pay-per-call REST API for public X (Twitter) data; no X
developer account is needed. This integration provides:

- `TwittrAPITweetSearch`: searches X with the operators of the X search box and returns each tweet as a
  `Document` (author, URL, time and engagement counts in `meta`), with the same `documents` and `links`
  outputs as the web-search components, plus `next_cursor` for paging.
- `TwittrAPIToolset`: 13 read-only X tools for Haystack Agents: search, profiles, timelines, followers,
  tweets with replies, quotes, retweets, Lists, Communities and trends.

## Installation

```bash
pip install twittrapi-haystack
```

Create an API key at [twittrapi.com](https://www.twittrapi.com) and set it as `TWITTRAPI_API_KEY`.
New accounts get test credit.

## TwittrAPITweetSearch

```python
from haystack_integrations.components.websearch.twittrapi import TwittrAPITweetSearch

search = TwittrAPITweetSearch(top_k=20)  # reads TWITTRAPI_API_KEY
result = search.run(query="haystack lang:en -filter:replies")

for doc in result["documents"]:
    print(doc.meta["author_username"], doc.meta["likes"], doc.content)
print(result["next_cursor"])  # pass as cursor= for the next page
```

The query takes the operators of the X search box: `from:user`, `to:user`, `"exact phrase"`,
`lang:en`, `since:2026-01-01`, `until:2026-02-01`, `min_faves:100`, `filter:media`,
`-filter:replies` and more.

**Parameters**

- `api_key`: TwittrAPI key. Defaults to the `TWITTRAPI_API_KEY` environment variable.
- `category`: `"Latest"` (default, newest first), `"Top"`, `"People"` (accounts instead of tweets),
  `"Photos"` or `"Videos"`. Can be changed per `run`.
- `top_k`: results per page, 1 to 100 (default 20).

**Outputs**

- `documents`: one `Document` per tweet. `content` is the full text; `meta` holds `id`, `url`,
  `created_at`, `lang`, `author_id`, `author_username`, `author_name`, `likes`, `retweets`,
  `replies`, `quotes`, `views` and `conversation_id`.
- `links`: the tweet URLs, in the same order.
- `next_cursor`: cursor for the next page, `None` on the last page.

### In a pipeline

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.websearch.twittrapi import TwittrAPITweetSearch

template = [
    ChatMessage.from_user(
        "Summarize what people say about {{ topic }} on X.\n"
        "{% for doc in documents %}- @{{ doc.meta.author_username }}: {{ doc.content }}\n{% endfor %}"
    )
]

pipe = Pipeline()
pipe.add_component("search", TwittrAPITweetSearch(top_k=30))
pipe.add_component("prompt", ChatPromptBuilder(template=template, required_variables=["topic", "documents"]))
pipe.add_component("llm", OpenAIChatGenerator(model="gpt-4o-mini"))
pipe.connect("search.documents", "prompt.documents")
pipe.connect("prompt.prompt", "llm.messages")

result = pipe.run({"search": {"query": "haystack lang:en"}, "prompt": {"topic": "Haystack"}})
print(result["llm"]["replies"][0].text)
```

## TwittrAPIToolset

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.tools.twittrapi import TwittrAPIToolset

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=TwittrAPIToolset(),  # reads TWITTRAPI_API_KEY
)
result = agent.run(messages=[ChatMessage.from_user("What has @deepset_ai posted this week?")])
print(result["messages"][-1].text)
```

| Tool | What it does |
| --- | --- |
| `search_tweets` | Search X with search operators; `People` returns accounts |
| `get_user_by_username` / `get_user_by_id` | A profile with counts and the numeric user ID |
| `get_user_tweets` | A user's recent tweets |
| `get_followers` / `get_following` | Followers and followed accounts |
| `get_tweet` | A tweet with its reply thread |
| `get_tweet_retweets` / `get_tweet_quotes` | Who retweeted a tweet, and the tweets quoting it |
| `get_list_tweets` | Latest tweets from an X List |
| `get_community_tweets` | Tweets in an X Community |
| `get_trends` / `get_trend_locations` | Trending topics by location (WOEID) |

Pick a subset with `TwittrAPIToolset(tool_names=["search_tweets", "get_user_tweets"])`. Results are
TwittrAPI's compact [simple format](https://www.twittrapi.com/docs/simple-format) (flat JSON), cut at
`max_chars` (default 20,000). Paginated tools print `next_cursor` first so the agent can page on. API
errors, such as an empty balance, are returned to the agent as the tool result.

## License

`twittrapi-haystack` is distributed under the terms of the [MIT](https://github.com/twittrapi/twittrapi-haystack/blob/main/LICENSE) license.
