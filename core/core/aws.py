import boto3
from core.settings import AWS_CREDENTIALS as AWS

s3 = boto3.client("s3",
    endpoint_url=AWS["AWS_URL"],
    aws_access_key_id=AWS["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=AWS["AWS_SECRET_ACCESS_KEY"]
)

ses = boto3.client("ses",
    endpoint_url=AWS["AWS_URL"],
    aws_access_key_id=AWS["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=AWS["AWS_SECRET_ACCESS_KEY"],
    region_name=AWS["AWS_SES_REGION_NAME"]
)

ses.verify_email_identity(
  EmailAddress = AWS["AWS_VERIFIED_EMAIL"]
)