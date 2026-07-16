#!/usr/bin/env bash
set -euo pipefail

echo "Checking AWS CLI..."
if ! command -v aws >/dev/null 2>&1; then
  echo "AWS CLI is not installed."
  echo "Install it first: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
  exit 1
fi

echo "AWS CLI version:"
aws --version

echo
echo "Configured identity:"
aws sts get-caller-identity

echo
echo "Configured region/profile:"
aws configure list

echo
echo "Prerequisite check complete."

