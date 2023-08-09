import json
import boto3
import os
import jwt
import time

def lambda_handler(event, context):
    try:
        token = jwt.decode(event['headers']['Authorization'].replace('Bearer ', ''), algorithms=['RS256'], options={"verify_signature": False})

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['USER_TABLE'])

        # Get user from event.pathParameters.username
        response = table.get_item(
            Key={
                'username': token['cognito:username']
            }
        )

        # Create response, if empty return 404
        if 'Item' not in response:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": "User not found"})
            }

        challenge_table = dynamodb.Table(os.environ['CHALLENGES_TABLE'])
        challenges = challenge_table.scan()

        response['Item']['points'] = 0
        for challenge_id in response['Item']['challenges_done']:
            # Filter to get the correct challenge
            t = list(filter(lambda x: x['challenge'] == challenge_id, challenges['Items']))
            if len(t) == 0:
                continue
            challenge = t[0]
            response['Item']['points'] += challenge['points']

        return {
            "statusCode": 200,
            "body": json.dumps(response['Item'], default=int)
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }

