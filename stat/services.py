from enum import Enum
from typing import ItemsView
import json
from botocore.exceptions import ClientError
from fastapi import status
from settings import init_db

db = init_db()

class DynamoDBFields(str, Enum):
    ITEM = "Item"
    ITEMS = "Items"
    ATTRS = "Attributes"
    ALL_NEW = "ALL_NEW"


def create_new_page(page):
    item = db.Table("Pages").get_item(Key={'id': page.id})
    if DynamoDBFields.ITEM in item:
        return "Page already exist.", status.HTTP_400_BAD_REQUEST

    put_item = {
        "id": str(page.id),
        "user_id": str(page.user_id),
        "name": page.name,
        "likes": 0,
        "followers": 0,
        "follow_requests": 0
    }

    db.Table("Pages").put_item(Item=put_item)

    return put_item, status.HTTP_200_OK


def update_page(page_name, user_id, page_id):
    item = db.Table("Pages").get_item(Key={'id': page_id})
    if not DynamoDBFields.ITEM in item:
        return "Undefined page.", status.HTTP_404_NOT_FOUND
    if item[DynamoDBFields.ITEM]["user_id"] != user_id:
        return "You have not permissions to perform this operation.", status.HTTP_400_BAD_REQUEST

    item = db.Table("Pages").update_item(
        Key={'id': page_id},
        UpdateExpression="SET #name = :n",
        ExpressionAttributeValues={
            ":n": page_name
        },
        ExpressionAttributeNames={
            "#name": "name"
        },
        ReturnValues=DynamoDBFields.ALL_NEW
    )

    return item[DynamoDBFields.ATTRS], status.HTTP_200_OK


def delete_page(user_id, page_id):
    item = db.Table("Pages").get_item(Key={'id': page_id})
    if not DynamoDBFields.ITEM in item:
        return "Undefined page.", status.HTTP_404_NOT_FOUND
    if item[DynamoDBFields.ITEM]["user_id"] != user_id:
        return "You have not permissions to perform this operation.", status.HTTP_400_BAD_REQUEST

    db.Table("Pages").delete_item(
        Key={'id': page_id}
    )

    return {"Status": "Deleted"}, status.HTTP_200_OK


def get_pages(user_id):
    response = db.Table("Pages").query(
        IndexName="user_id",
        KeyConditionExpression="user_id=:user_id",
        ExpressionAttributeValues={
            ":user_id": user_id
        }
    )
    return response[DynamoDBFields.ITEMS], status.HTTP_200_OK


def new_like(page_id):
    item = db.Table("Pages").get_item(Key={'id': page_id})
    if not DynamoDBFields.ITEM in item:
        return "Undefined page.", status.HTTP_404_NOT_FOUND
    item = db.Table("Pages").update_item(
        Key={'id': page_id},
        UpdateExpression="ADD likes :inc",
        ExpressionAttributeValues={
            ":inc": 1
        },
        ReturnValues=DynamoDBFields.ALL_NEW
    )

    return item[DynamoDBFields.ATTRS], status.HTTP_200_OK


def new_follower(page_id):
    item = db.Table("Pages").get_item(Key={'id': page_id})
    if not DynamoDBFields.ITEM in item:
        return "Undefined page.", status.HTTP_404_NOT_FOUND
    item = db.Table("Pages").update_item(
        Key={'id': page_id},
        UpdateExpression="ADD followers :inc",
        ExpressionAttributeValues={
            ":inc": 1
        },
        ReturnValues=DynamoDBFields.ALL_NEW
    )

    return item[DynamoDBFields.ATTRS], status.HTTP_200_OK


def new_follow_request(page_id):
    item = db.Table("Pages").get_item(Key={'id': page_id})
    if not DynamoDBFields.ITEM in item:
        return "Undefined page.", status.HTTP_404_NOT_FOUND
    item = db.Table("Pages").update_item(
        Key={'id': page_id},
        UpdateExpression="ADD follow_requests :inc",
        ExpressionAttributeValues={
            ":inc": 1
        },
        ReturnValues=DynamoDBFields.ALL_NEW
    )

    return item[DynamoDBFields.ATTRS], status.HTTP_200_OK


def undo_like(page_id):
    item = db.Table("Pages").get_item(Key={'id': page_id})
    if not DynamoDBFields.ITEM in item:
        return "Undefined page.", status.HTTP_404_NOT_FOUND
    try:
        item = db.Table("Pages").update_item(
            Key={'id': page_id},
            UpdateExpression="ADD likes :inc",
            ConditionExpression="likes > :zero",
            ExpressionAttributeValues={
                ":inc": -1,
                ":zero": 0
            },
            ReturnValues=DynamoDBFields.ALL_NEW
        )
    except ClientError as err:
        if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return "Cannot undo like action because likes count already equals to 0.", status.HTTP_400_BAD_REQUEST
        raise err

    return item[DynamoDBFields.ATTRS], status.HTTP_200_OK


def undo_follower(page_id):
    item = db.Table("Pages").get_item(Key={'id': page_id})
    if not DynamoDBFields.ITEM in item:
        return "Undefined page.", status.HTTP_404_NOT_FOUND
    try:
        item = db.Table("Pages").update_item(
            Key={'id': page_id},
            UpdateExpression="ADD followers :inc",
            ConditionExpression="followers > :zero",
            ExpressionAttributeValues={
                ":inc": -1,
                ":zero": 0
            },
            ReturnValues=DynamoDBFields.ALL_NEW
        )
    except ClientError as err:
        if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return "Cannot undo follower action because followers count already equals to 0.", status.HTTP_400_BAD_REQUEST
        raise err

    return item[DynamoDBFields.ITEM], status.HTTP_200_OK


def undo_follow_request(page_id):
    item = db.Table("Pages").get_item(Key={'id': page_id})
    if not DynamoDBFields.ITEM in item:
        return "Undefined page.", status.HTTP_404_NOT_FOUND
    try:
        item = db.Table("Pages").update_item(
            Key={'id': page_id},
            UpdateExpression="ADD follow_requests :inc",
            ConditionExpression="follow_requests > :zero",
            ExpressionAttributeValues={
                ":inc": -1,
                ":zero": 0
            },
            ReturnValues=DynamoDBFields.ALL_NEW
        )
    except ClientError as err:
        if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return "Cannot undo follow request action because follow requests count already equals to 0.", status.HTTP_400_BAD_REQUEST
        raise err

    return item[DynamoDBFields.ITEM], status.HTTP_200_OK
