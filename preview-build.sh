#!/bin/bash
set -euo pipefail

HUGO_VERSION="0.155.2"
curl -fsSL "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.tar.gz" -o hugo.tar.gz
tar -xzf hugo.tar.gz hugo
export PATH="$PWD:$PATH"

rm -rf _site
git clone --depth=1 https://github.com/deepset-ai/haystack-home.git _site
cd _site

cp ../integrations/*.md content/integrations/
mkdir -p static/logos
cp -R ../logos/* static/logos/

npm install

PREVIEW_URL="${VERCEL_URL:-localhost}"
hugo -b "https://${PREVIEW_URL}"
