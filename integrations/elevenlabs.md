---
layout: integration
name: Elevenlabs
description: ElevenLabs Text-to-Speech components for Haystack.
authors:
    - name: Andy
      socials:
        github: andychert
        twitter: andychert
pypi: https://pypi.org/project/elevenlabs-haystack/
repo: https://github.com/andychert/elevenlabs-haystack
type: Model Provider
report_issue: https://github.com/andychert/elevenlabs-haystack/issues
logo: /logos/elevenlabs.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

This repository contains an integration of ElevenLabs' Text-to-Speech API with Haystack pipelines. This package allows you to convert text to speech using ElevenLabs' API and optionally save the generated audio to AWS S3.

## Installation

```bash
pip install elevenlabs_haystack
```

## Usage

#### **ElevenLabs API Key**

To access the ElevenLabs API, you need to create an account and obtain an API key.

1. Go to the [ElevenLabs](https://elevenlabs.ai/) website and sign up for an account.
2. Once logged in, navigate to the **Profile** section.
3. In the **API** section, generate a new API key.
4. Copy the API key.

#### **AWS Credentials**

To store generated audio files on AWS S3, you need AWS credentials (Access Key ID, Secret Access Key) and specify a region.

1. If you don’t have an AWS account, sign up at [AWS](https://aws.amazon.com/).
2. Create a new IAM user and assign the necessary permissions to allow the user to upload files to S3. The `AmazonS3FullAccess` policy is sufficient for this example.
3. Once the IAM user is created, download or note the **AWS Access Key ID** and **Secret Access Key**.
4. Identify the **AWS Region** where your S3 bucket resides (e.g., `us-east-1`). This information can be found in the AWS Management Console.
5. Finally, create or identify the S3 bucket where the generated audio files will be saved.

Create a `.env` file in the root directory with the following content (replace with your actual credentials):

```bash
ELEVENLABS_API_KEY=sk_your_elevenlabs_api_key_here
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION_NAME=us-east-1
AWS_S3_BUCKET_NAME=your_s3_bucket_name
```

These variables will be automatically loaded using `dotenv` and used to access ElevenLabs and AWS services securely.

### Basic Text-to-Speech Example

This example shows how to use the `ElevenLabsTextToSpeech` component to convert text to speech and save the generated audio file locally or in an AWS S3 bucket. It uses environment variables to access sensitive credentials.

```python
from haystack.utils import Secret
from elevenlabs_haystack import ElevenLabsTextToSpeech

# Initialize the ElevenLabsTextToSpeech component using environment variables for sensitive data
tts = ElevenLabsTextToSpeech(
    elevenlabs_api_key=Secret.from_env_var("ELEVENLABS_API_KEY"),
    output_folder="audio_files",  # Save the generated audio locally
    voice_id="Alice",  # ElevenLabs voice ID
    aws_s3_bucket_name=Secret.from_env_var("AWS_S3_BUCKET_NAME"),  # S3 bucket for optional upload
    aws_s3_output_folder="s3_files",  # Save the generated audio to AWS S3
    aws_access_key_id=Secret.from_env_var("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=Secret.from_env_var("AWS_SECRET_ACCESS_KEY"),
    aws_region_name=Secret.from_env_var("AWS_REGION_NAME"),  # AWS region
    voice_settings={
        "stability": 0.75,
        "similarity_boost": 0.75,
        "style": 0.5,
        "use_speaker_boost": True,  # Optional voice settings
    },
)

# Run the text-to-speech conversion
result = tts.run("Hello, world!")

# Print the result
print(result)

"""
{
    "id": "elevenlabs-id",
    "file_name": "audio_files/elevenlabs-id.mp3",
    "s3_file_name": "s3_files/elevenlabs-id.mp3",
    "s3_bucket_name": "test-bucket",
    "s3_presigned_url": "https://test-bucket.s3.amazonaws.com/s3_files/elevenlabs-id.mp3"
}
"""
```

### Example Using Haystack Pipeline

This example demonstrates how to integrate the `ElevenLabsTextToSpeech` component into a Haystack pipeline. Additionally, we define a `WelcomeTextGenerator` component that generates a personalized welcome message.

```python
from haystack import component, Pipeline
from haystack.utils import Secret
from elevenlabs_haystack import ElevenLabsTextToSpeech

# Define a simple component to generate a welcome message
@component
class WelcomeTextGenerator:
    """
    A component generating a personal welcome message and making it upper case.
    """
    @component.output_types(welcome_text=str, note=str)
    def run(self, name: str):
        return {
            "welcome_text": f'Hello {name}, welcome to Haystack!'.upper(),
            "note": "welcome message is ready"
        }

# Create a Pipeline
text_pipeline = Pipeline()

# Add WelcomeTextGenerator to the Pipeline
text_pipeline.add_component(
    name="welcome_text_generator",
    instance=WelcomeTextGenerator()
)

# Add ElevenLabsTextToSpeech to the Pipeline using environment variables
text_pipeline.add_component(
    name="tts",
    instance=ElevenLabsTextToSpeech(
        elevenlabs_api_key=Secret.from_env_var("ELEVENLABS_API_KEY"),
        output_folder="audio_files",  # Save the generated audio locally
        voice_id="Alice",  # ElevenLabs voice ID
        aws_s3_bucket_name=Secret.from_env_var("AWS_S3_BUCKET_NAME"),  # S3 bucket for optional upload
        aws_s3_output_folder="s3_files",  # Save the generated audio to AWS S3
        aws_access_key_id=Secret.from_env_var("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=Secret.from_env_var("AWS_SECRET_ACCESS_KEY"),
        aws_region_name=Secret.from_env_var("AWS_REGION_NAME"),  # Load region from env
        voice_settings={
            "stability": 0.75,
            "similarity_boost": 0.75,
            "style": 0.5,
            "use_speaker_boost": True,  # Optional voice settings
        },
    ),
)

# Connect the output of WelcomeTextGenerator to the input of ElevenLabsTextToSpeech
text_pipeline.connect(sender="welcome_text_generator.welcome_text", receiver="tts")

# Run the pipeline with a sample name
result = text_pipeline.run({"welcome_text_generator": {"name": "Bilge"}})

# Print the result
print(result)

"""
{
    "id": "elevenlabs-id",
    "file_name": "audio_files/elevenlabs-id.mp3",
    "s3_file_name": "s3_files/elevenlabs-id.mp3",
    "s3_bucket_name": "test-bucket",
    "s3_presigned_url": "https://test-bucket.s3.amazonaws.com/s3_files/elevenlabs-id.mp3"
}
"""
```

# License

This project is licensed under the MIT License.
