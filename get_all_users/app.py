import json
import boto3
import os
# import requests


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['USER_TABLE'])
    challenge_table = dynamodb.Table(os.environ['CHALLENGES_TABLE'])

    # Get all users
    users = table.scan()
    challenges = challenge_table.scan()

    for user in users['Items']:
        user['points'] = 0
        for challenge_id in user['challenges_done']:
            # Filter to get the correct challenge
            t = list(filter(lambda x: x['challenge'] == challenge_id, challenges['Items']))
            if len(t) == 0:
                continue
            challenge = t[0]
            user['points'] += challenge['points']

    return {
        "statusCode": 200,
        "body": json.dumps(users['Items'], default=int)
    }
