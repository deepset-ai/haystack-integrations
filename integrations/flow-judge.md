---
layout: integration
name: Flow Judge
description: Evaluate Haystack pipelines using Flow Judge
authors:
    - name: Flow AI
      socials:
        github: flowaicom
        twitter: flowaicom
        linkedin: https://www.linkedin.com/company/flowaicom/ 
pypi: https://pypi.org/project/flow-judge/
repo: https://github.com/flowaicom/flow-judge
type: Evaluation Framework
report_issue: https://github.com/flowaicom/flow-judge/issues
logo: /logos/flow-ai.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview
This integration allows you to evaluate Haystack pipelines using Flow Judge.

Flow Judge is an open-source, lightweight (3.8B) language model optimized for LLM system evaluations. Crafted for accuracy, speed, and customization.

Read the technical report [here](https://www.flow-ai.com/blog/flow-judge).

## Installation

For running Flow Judge with vLLM engine:
```bash
pip install flow-judge[vllm]
pip install 'flash_attn>=2.6.3' --no-build-isolation
```
For running Flow Judge with transformers:
```bash
pip install flow-judge[hf]
```
If flash attention:
```bash
pip install 'flash_attn>=2.6.3' --no-build-isolation
```
For running Flow Judge with Llamafile on macOS:
```bash
pip install flow-judge[llamafile]
pip install 'flash_attn>=2.6.3' --no-build-isolation
```
To learn more about the installation, visit the [Flow Judge Installation](https://pypi.org/project/flow-judge/) page.

Finally install Haystack:
```bash
pip install haystack-ai
```

## Usage 
Flow Judge integration with Haystack is designed to facilitate the evaluation of Haystack pipelines using Flow Judge. This integration allows you to seamlessly integrate Flow Judge into your Haystack workflows, enabling you to evaluate and improve your LLM systems with precision and efficiency. 

Flow Judge offers a set-of built-in metrics and easy-to-create custom metrics. 

### Available Built-in Metrics  

Built-in metrics come with 3 different scoring scales Binary, 3-point Likert and 5-point Likert: 
- Response Correctness
- Response Faithfulness
- Response Relevance  

To check the available metrics you can run:
```python
from flow_judge.metrics import list_all_metrics
list_all_metrics()
```

While these preset metrics provide a solid foundation for evaluation, the true power of Flow Judge lies in its ability to create custom metrics tailored to your specific requirements. This flexibility allows for a more nuanced and comprehensive assessment of your LLM systems.

### Components
This integration introduces `HaystackFlowJudge` component, which is used just like other evaluator components in Haystack. 

For details about the use and parameters of this component please refer to [HaystackFlowJudge class](https://github.com/flowaicom/flow-judge/blob/main/flow_judge/integrations/haystack.py) and Haystack's [LLMEvaluator component](https://docs.haystack.deepset.ai/reference/evaluators-api#module-llm_evaluator).
  
### Use Flow Judge with Haystack 
We have created a comprehensive guide on how to effectively use Flow Judge with Haystack. You can access it [here](https://github.com/flowaicom/flow-judge/blob/main/examples/5_evaluate_haystack_rag_pipeline.ipynb). This tutorial demonstrates how to evaluate a RAG pipeline built with Haystack using Flow Judge. 

### Quick Example
The code snippet below provides a simpler example of how to integrate Flow Judge with Haystack. However, we recommend following the full tutorial for a deeper understanding of the concepts and implementation. 

```python
from flow_judge.integrations.haystack import HaystackFlowJudge
from flow_judge.metrics.presets import RESPONSE_FAITHFULNESS_5POINT
from flow_judge import Hf

from haystack import Pipeline

# Create a model using Hugging Face Transformers with Flash Attention
model = Hf() # We support also Vllm, Llamafile

# Evaluation sample 
questions = ["What is the termination clause in the contract?"] 
contexts = ["This contract may be terminated by either party upon providing thirty (30) days written notice to the other party. In the event of a breach of contract, the non-breaching party may terminate the contract immediately."]
answers = ["The contract can be terminated by either party with thirty days written notice."] 

# Define the HaystackFlowJudge evaluator, we will use the built-in metric for faithfulness 
# For parameters refer to Haystack's [LLMEvaluator](https://docs.haystack.deepset.ai/reference/evaluators-api#module-llm_evaluator) and HaystackFlowJudge class. 
ff_evaluator = HaystackFlowJudge(
    metric=RESPONSE_FAITHFULNESS_5POINT,
    model=model,
    progress_bar=True,
    raise_on_failure=True,
    save_results=True,
    fail_on_parse_error=False
)

# Setup the pipeline
eval_pipeline = Pipeline()

# Add components to the pipeline
eval_pipeline.add_component("ff_evaluator", ff_evaluator)

# Run the eval pipeline
results = eval_pipeline.run(
    {
        "ff_evaluator": {
            'query': questions,
            'context': contexts,
            'response': answers,
        }
    }
)

# Print eval results 
for result in results['ff_evaluator']['results']:
    score = result['score']
    feedback = result['feedback']
    print(f"Score: {score}")
    print(f"Feedback: {feedback}\n")

``` 

### License
The code is licensed under the [Apache 2.0 license.](https://github.com/flowaicom/flow-judge/blob/main/LICENSE)

