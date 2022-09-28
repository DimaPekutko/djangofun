import os
import boto3
from dotenv import load_dotenv
load_dotenv()


IS_PRODUCTION = os.getenv("DEBUG", "False") == "False"

AWS_CREDENTIALS = {
    "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
    "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
    "AWS_URL": f"http://{os.getenv('AWS_HOST')}:{os.getenv('AWS_PORT')}",
    "AWS_SES_REGION_NAME": os.getenv("AWS_SES_REGION_NAME"),
}


def init_db():
    db = boto3.resource("dynamodb",
                        endpoint_url=AWS_CREDENTIALS["AWS_URL"],
                        aws_access_key_id=AWS_CREDENTIALS["AWS_ACCESS_KEY_ID"],
                        aws_secret_access_key=AWS_CREDENTIALS["AWS_SECRET_ACCESS_KEY"],
                        region_name=AWS_CREDENTIALS["AWS_SES_REGION_NAME"]
                        )

    # create Pages table in development mode
    if len(list(db.tables.all())) < 1 and not IS_PRODUCTION:
        db.create_table(
            TableName="Pages",
            AttributeDefinitions=[
                {
                    "AttributeName": "id",
                    "AttributeType": "S"
                },
                {
                    "AttributeName": "user_id",
                    "AttributeType": "S"
                },
            ],
            ProvisionedThroughput={
                "WriteCapacityUnits": 5,
                "ReadCapacityUnits": 5
            },
            KeySchema=[
                {
                    "AttributeName": "id",
                    "KeyType": "HASH"
                },
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "user_id",
                    "KeySchema": [
                        {
                            "AttributeName": "user_id",
                            "KeyType": "HASH"
                        }
                    ],
                    "Projection": {
                        "ProjectionType": "ALL"
                    },
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 1,
                        "WriteCapacityUnits": 1
                    }
                }
            ]
        )
    return db
