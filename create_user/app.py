import json
import boto3
import os
# import requests


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['USER_TABLE'])

    body = json.loads(event["body"])

    if 'mail' not in body:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Mail is required"})
        }

    # Get username from event.pathParameters.username
    # Create user
    response = table.put_item(
        Item={
            'username': event['pathParameters']['username'],
            'mail': body['mail']
        }
    )

    # Check if creation was successful
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Could not create user"})
        }

    # Create response
    return {
        "statusCode": 200,
        "body": json.dumps({"success": "User created"})
    }

