#!/bin/bash
set -euo pipefail

HUGO_VERSION="0.155.2"
wget -q "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.tar.gz"
tar -xzf "hugo_extended_${HUGO_VERSION}_linux-amd64.tar.gz" hugo
export PATH="$PWD:$PATH"

git clone --depth=1 https://github.com/deepset-ai/haystack-home.git _site
cd _site

cp ../integrations/*.md content/integrations/
cp -R ../logos/* static/logos/ 2>/dev/null || true

npm install

PREVIEW_URL="${VERCEL_URL:-localhost}"
hugo -b "https://${PREVIEW_URL}"
