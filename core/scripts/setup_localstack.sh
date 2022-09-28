#!/bin/bash

# awslocal dynamodb create-table --cli-input-json file:///tabledef.json
awslocal s3 mb s3://$AWS_BUCKET_NAME