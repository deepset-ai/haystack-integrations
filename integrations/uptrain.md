---
layout: integration
name: UpTrain
description: Use the UpTrain evaluation framework to calculate model-based metrics 
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/uptrain-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/uptrain
type: Evaluation Framework
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/uptrain.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
    - [UpTrainEvaluator](#UpTrainEvaluator)

## Overview

[UpTrain](https://uptrain.ai/) is an open source framework for model-based evaluation to evaluate your LLM applications by quantifying their performance on aspects such as correctness, tonality, hallucination, fluency, etc. More information can be found on the [documentation page](https://docs.haystack.deepset.ai/v2.0/docs/uptrainevaluator).

## Installation

Install the UpTrain integration:
```bash
pip install uptrain-haystack
```

## Usage

Once installed, you will have access to an [UpTrainEvaluator](https://docs.haystack.deepset.ai/v2.0/docs/uptrainevaluator) that supports a variety of model-based evaluation metrics: 
- "context_relevance"
- "factual_accuracy"
- "response_relevance"
- "response_completeness"
- "response_completeness_wrt_context"
- "response_consistency"
- "response_conciseness"
- "critique_language"
- "critique_tone"
- "guideline_adherence"
- "response_matching"

### UpTrainEvaluator

To use this integration for calculating model-based evaluation metrics, initialize an `UpTrainEvaluator` with the metric name and metric input parameters: 

```python
from haystack import Pipeline
from haystack_integrations.components.evaluators import UpTrainEvaluator, UpTrainMetric

QUESTIONS = [
    "Which is the most popular global sport?",
]
CONTEXTS = [
    "The popularity of sports can be measured in various ways, including TV viewership, social media presence, number of participants, and economic impact. Football is undoubtedly the world's most popular sport with major events like the FIFA World Cup and sports personalities like Ronaldo and Messi, drawing a followership of more than 4 billion people."
]
RESPONSES = [
    "Football is the most popular sport with around 4 billion followers worldwide",
]

pipeline = Pipeline()
evaluator = UpTrainEvaluator(
    metric=UpTrainMetric.FACTUAL_ACCURACY,
    api="openai",
    api_key_env_var="OPENAI_API_KEY",
)
pipeline.add_component("evaluator", evaluator)

# Each metric expects a specific set of parameters as input. Refer to the
# UpTrainMetric class' documentation for more details.
output = pipeline.run({"evaluator": {"questions": QUESTIONS, "contexts": CONTEXTS, "responses": RESPONSES}})

for output in output["evaluator"]["results"]:
    print(output)
```
Output: 
```python
[{'name': 'factual_accuracy', 'score': 1.0, 'explanation': "1. Football is the most popular sport.\nReasoning for yes: The context explicitly states that football is undoubtedly the world's most popular sport.\nReasoning for no: No arguments.\nJudgement: yes. as the context explicitly supports the fact.\n\n2. Football has around 4 billion followers worldwide.\nReasoning for yes: The context explicitly mentions that major events like the FIFA World Cup and sports personalities like Ronaldo and Messi draw a followership of more than 4 billion people.\nReasoning for no: No arguments.\nJudgement: yes. as the context explicitly supports the fact.\n\n"}]
```
