---
layout: integration
name: Answer and Document to Speech
description: 
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/farm-haystack-text2speech/
repo: https://github.com/deepset-ai/haystack-extras/tree/main/nodes/text2speech
type: Custom Node
report_issue: https://github.com/deepset-ai/haystack-extras/issues
---

# AnswerToSpeech and DocumentToSpeech

The `farm-haystack-text2speech` package contains two Nodes that allow you to convert Haystack `Answers` and `Documents` into audio files: `AnswerToSpeech` and `DocumentToSpeech`.

## Installation

For Debain-based systems, first install some more dependencies:
```bash
sudo apt-get install libsndfile1 ffmpeg
```

Install the `text2speech` package:
```bash
pip install farm-haystack-text2speech`
```

## Usage

For a full example of how to use the `AnswerToSpeech` Node, you may try out our "[Make Your QA Pipelines Talk Tutorial](https://haystack.deepset.ai/tutorials/17_audio)"

For example, in a simple Extractive QA Pipeline:

```
from haystack.nodes import BM25Retriever, FARMReader
from text2speech import AnswerToSpeech

retriever = BM25Retriever(document_store=document_store)
reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)
answer2speech = AnswerToSpeech(
    model_name_or_path="espnet/kan-bayashi_ljspeech_vits", generated_audio_dir=Path("./audio_answers")
)

audio_pipeline = Pipeline()
audio_pipeline.add_node(retriever, name="Retriever", inputs=["Query"])
audio_pipeline.add_node(reader, name="Reader", inputs=["Retriever"])
audio_pipeline.add_node(answer2speech, name="AnswerToSpeech", inputs=["Reader"])
```