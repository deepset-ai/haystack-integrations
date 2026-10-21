---
layout: integration
name: "YouTube Download to Cloud Storage — FlashData"
description: "Track a YouTube delivery to customer cloud storage with a source-specific Haystack component."
authors:
  - name: FlashData
    socials:
      github: rocosen
repo: https://github.com/rocosen/flashdata-mcp
report_issue: https://github.com/rocosen/flashdata-mcp/issues
type: Data Ingestion
version: Haystack 3.4
toc: true
---

## Track a YouTube delivery to customer cloud storage

Submit an authorized asynchronous video or audio delivery to customer storage, then inspect the saved job without submitting it again. Separate submit, status and result components keep the storage write explicit.

This integration uses the `youtube_download` FlashData source. See the
[YouTube Download to Cloud Storage setup, request fields and pricing](https://flashdata.dev/docs/sources/youtube_download)
to create an account and API key before running it.

## Install and configure

Requires Python 3.11+ and Haystack 3.4. The package is installed from a versioned source tag;
there is no published PyPI release at this stage.

```bash
pip install "git+https://github.com/rocosen/flashdata-mcp.git@haystack-v0.1.0#subdirectory=packages/haystack"
```

Set `FLASHDATA_API_KEY` through your environment or secret manager. Never place a real key in
source code, an agent prompt, pipeline YAML, or a public issue. Components also accept a Haystack
`Secret.from_env_var("YOUR_KEY_VARIABLE")`. No model key is needed for the example below.

## Run a pipeline

```python
from haystack import Pipeline
from flashdata_haystack import FlashDataYouTubeDownloadStatus

pipe = Pipeline()
pipe.add_component("delivery", FlashDataYouTubeDownloadStatus())
# Replace with the receipt from an earlier authorized submission.
result = pipe.run({"delivery": {"job_id": "job_REPLACE-WITH-SAVED-RECEIPT"}})
print(result["delivery"]["result"])
```

### Inputs and outputs

- Inputs: submit: video_id, optional format/quality/clip fields; reads: job_id. Storage comes from FLASHDATA_DOWNLOAD_STORAGE.
- API output: submit: id/status receipt; reads: job lifecycle; completed result: output JSON delivery manifest.
- `result` preserves the API response, with credential-free lifecycle fields for job reads.

- Inspect `FlashDataYouTubeDownloadStatus.input_model.model_json_schema()` for all supported types, ranges and defaults without making a request.


### Submit once, then read the receipt

Use only videos you have rights to process. Configure a customer-owned storage destination using
`FLASHDATA_DOWNLOAD_STORAGE` (the JSON `params.storage` object documented in the source guide).
Supported providers are S3, S3-compatible storage, GCS, Azure, OSS, COS, BOS and TOS.
Storage credentials stay in the operator environment and are excluded from tool input schemas and serialized pipelines.

```python
from flashdata_haystack import FlashDataYouTubeDownloadSubmit, FlashDataYouTubeDownloadResult

# Explicitly opt in only after authorizing the API charge and customer-storage write.
submit = FlashDataYouTubeDownloadSubmit(allow_submit=True)
receipt = submit.run(video_id="YOUR_VIDEO_ID", download_type="audio", output_format="m4a")["result"]
print(receipt)  # Save this id before doing anything else.

# At a later time, read the same id. Never call submit again to poll.
result = FlashDataYouTubeDownloadResult().run(job_id=receipt["id"])
print(result["result"])
```

Submit is disabled by default. Status/result never submit or automatically poll.
A completed result reader validates the management API's HTTPS result origin and sends no API key
to the signed result URL. Lifecycle output omits job parameters that could contain storage credentials.
The result manifest may contain signed URLs: share it only with intended recipients.

## Use with an agent

```python
from flashdata_haystack import FlashDataYouTubeDownloadStatus, as_tool

tool = as_tool(FlashDataYouTubeDownloadStatus())
print(tool.parameters)  # Source-specific schema; no API or model call.
# Add `tool` to your existing Haystack Agent's tools list.
```

The agent chooses when and how to use the tool. Keep credentials and, for delivery, the decision
to enable submission in operator configuration. Tool output is the JSON `result`; no model,
embedding service, scraper or vector database is included.

## Save and load

```python
saved = pipe.dumps()
restored = Pipeline.loads(saved, allowed_modules=["flashdata_haystack"])
```

Only environment variable names are serialized, never their secret values. Token-based Haystack
Secrets deliberately cannot be serialized. Load only pipeline definitions you have reviewed.

## Cost, limits and errors

Installation is free under MIT. **FlashData API requests consume paid Credits**; see the
[source guide](https://flashdata.dev/docs/sources/youtube_download) for its current rate and
[FlashData pricing](https://flashdata.dev/pricing). Any downstream model or cloud-storage charges are separate.

Paid asynchronous job. Requires customer storage. Save the receipt; never submit again to poll. Result JSON expires after 24 hours; media retention depends on storage.

Invalid input fails before sending a request. Requests have a 120-second network timeout
(15 seconds to connect), a 20 MiB response limit and no automatic retries. A timeout after
submission can have an unknown billing outcome: inspect Jobs in your FlashData account before
submitting again. Authentication, insufficient Credits and rate limits raise `FlashDataError`
without embedding raw responses or credentials. Empty results remain empty.

## Source and license

[Implementation and all component examples](https://github.com/rocosen/flashdata-mcp/tree/haystack-v0.1.0/packages/haystack)
are maintained by FlashData under the MIT license. This is a community integration;
publication in the Haystack directory is subject to its maintainers' review.
