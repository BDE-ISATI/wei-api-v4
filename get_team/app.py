import json
import boto3
import os

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TEAMS_TABLE'])

    # Get user from event.pathParameters.username
    response = table.get_item(
        Key={
            'team': event['pathParameters']['team']
        }
    )

    # Create response, if empty return 404
    if 'Item' not in response:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Team not found"})
        }

    return {
        "statusCode": 200,
        "body": json.dumps(response['Item'])
    }

