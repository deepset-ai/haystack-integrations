---
layout: integration
name: UpTrain
description: Use the UpTrain evaluation framework to calculate metrics 
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
from uptrain_haystack import UpTrainEvaluator, UpTrainMetric

evaluator = UpTrainEvaluator(metric=UpTrainMetric.FACTUAL_ACCURACY, ...)
result = evaluator.run(...)
```
Output: 
```shell
'...'
```
