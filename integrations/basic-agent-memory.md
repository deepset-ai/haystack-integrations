---
layout: integration
name: Basic Agent Memory
description: A working memory that stores the Agent's conversation memory
authors:
    - name: Roland Tannous
      socials:
        github: rolandtannous
        twitter: rolandtannous
    - name: Xceron
      socials:
        github: Xceron
pypi: https://pypi.org/project/haystack-memory/
repo: https://github.com/rolandtannous/haystack-memory
type: Agent Tool
report_issue: https://github.com/rolandtannous/haystack-memory/issues
---

# Basic Haystack Memory Tool

This library implements a working memory that stores the Agent's conversation memory 
and a sensory memory that stores the agent's short-term sensory memory. The working memory can be utilized in-memory or through Redis, with the 

Redis implementation featuring a sliding window. On the other hand, the sensory memory is an in-memory implementation that mimics 
a human's brief sensory memory, lasting only for the duration of one interaction.. 

## Installation

- Python pip: ```pip install --upgrade haystack-memory``` . This method will attempt to install the dependencies (farm-haystack>=1.15.0, redis)
- Python pip (skip dependency installation): Use  ```pip install --upgrade haystack-memory --no-deps```
- Using git: ```pip install git+https://github.com/rolandtannous/haystack-memory.git@main#egg=haystack-memory```


## Usage

To use memory in your agent, you need three components:
- `MemoryRecallNode`: This node is added to the agent as a tool. It will allow the agent to remember the conversation and make query-memory associations.
- `MemoryUtils`: This class should be used to save the queries and the final agent answers to the conversation memory.
- `chat`: This is a method of the MemoryUtils class. It is used to chat with the agent. It will save the query and the answer to the memory. It also returns the full result for further usage.

```py
from haystack.agents import Agent, Tool
from haystack.nodes import PromptNode
from haystack_memory.prompt_templates import memory_template
from haystack_memory.memory import MemoryRecallNode
from haystack_memory.utils import MemoryUtils

# Initialize the memory and the memory tool so the agent can retrieve the memory
working_memory = []
sensory_memory = []
memory_node = MemoryRecallNode(memory=working_memory)
memory_tool = Tool(name="Memory",
                   pipeline_or_node=memory_node,
                   description="Your memory. Always access this tool first to remember what you have learned.")

prompt_node = PromptNode(model_name_or_path="text-davinci-003", 
                         api_key="<YOUR_OPENAI_KEY>", 
                         max_length=1024,
                         stop_words=["Observation:"])
memory_agent = Agent(prompt_node=prompt_node, prompt_template=memory_template)
memory_agent.add_tool(memory_tool)

# Initialize the utils to save the query and the answers to the memory
memory_utils = MemoryUtils(working_memory=working_memory,sensory_memory=sensory_memory, agent=memory_agent)
result = memory_utils.chat("<Your Question>")
print(working_memory)
```

### Redis

The working memory can also be stored in a redis database which makes it possible to use different memories at the same time to be used with multiple agents. Additionally, it supports a sliding window to only utilize the last k messages.

```py
from haystack.agents import Agent, Tool
from haystack.nodes import PromptNode
from haystack_memory.memory import RedisMemoryRecallNode
from haystack_memory.prompt_templates import memory_template
from haystack_memory.utils import RedisUtils

sensory_memory = []
# Initialize the memory and the memory tool so the agent can retrieve the memory
redis_memory_node = RedisMemoryRecallNode(memory_id="working_memory",
                                          host="localhost",
                                          port=6379,
                                          db=0)
memory_tool = Tool(name="Memory",
                   pipeline_or_node=redis_memory_node,
                   description="Your memory. Always access this tool first to remember what you have learned.")
prompt_node = PromptNode(model_name_or_path="text-davinci-003",
                         api_key="<YOUR_OPENAI_KEY>",
                         max_length=1024,
                         stop_words=["Observation:"])
memory_agent = Agent(prompt_node=prompt_node, prompt_template=memory_template)
# Initialize the utils to save the query and the answers to the memory
redis_utils = RedisUtils(agent=memory_agent,
                         sensory_memory=sensory_memory,
                         memory_id="working_memory",
                         host="localhost",
                         port=6379,
                         db=0)
result = redis_utils.chat("<Your Question>")
```


## Examples

Examples can be found in the `examples/` folder. They contain usage examples for both in-memory and Redis memory types.
To open the examples in colab, click on the following links:
- Basic Memory: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rolandtannous/HaystackAgentBasicMemory/blob/main/examples/example_basic_memory.ipynb)
- Redis Memory: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rolandtannous/HaystackAgentBasicMemory/blob/main/examples/example_redis_memory.ipynb)






