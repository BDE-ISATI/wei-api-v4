import json
import boto3
import os
# import requests


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['CHALLENGES_TABLE'])

    # Get user from event.pathParameters.username
    response = table.get_item(
        Key={
            'challenge_id': event['pathParameters']['challenge_id']
        }
    )

    # Create response, if empty return 404
    if 'Item' not in response:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Challenge not found"})
        }

    return {
        "statusCode": 200,
        "body": json.dumps(response['Item'])
    }

