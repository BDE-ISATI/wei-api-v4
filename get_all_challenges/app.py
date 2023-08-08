import json
import boto3
import os
# import requests


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['CHALLENGES_TABLE'])

    # Get all users
    response = table.scan()

    # Create response
    return {
        "statusCode": 200,
        "body": json.dumps(response['Items'], default=int)
    }
