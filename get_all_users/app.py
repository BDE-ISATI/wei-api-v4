import boto3
import json
import os
import time

cache = None
cache_time = 0


def lambda_handler(event, context):
    global cache
    global cache_time

    if not (event['queryStringParameters'] and 'force_refresh' in event['queryStringParameters']) and (
            cache is not None and time.time() < cache_time + int(os.environ['CACHE_TIME'])):
        return cache

    try:
        dynamodb = boto3.resource('dynamodb')

        user_table = dynamodb.Table(os.environ['USER_TABLE'])
        users = user_table.scan()
        if users['ResponseMetadata']['HTTPStatusCode'] != 200 or 'Items' not in users:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error retrieving users', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }
        users = users['Items']

        challenge_table = dynamodb.Table(os.environ['CHALLENGES_TABLE'])
        challenges = challenge_table.scan()
        if challenges['ResponseMetadata']['HTTPStatusCode'] != 200 or 'Items' not in challenges:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error retrieving challenges', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }
        challenges = challenges['Items']

        for user in users:
            user['points'] = 0
            for challenge_id in user['challenges_done']:
                # Filter to get the correct challenge
                t = list(filter(lambda x: x['challenge'] == challenge_id, challenges))
                if len(t) == 0:
                    continue
                challenge = t[0]
                user['points'] += challenge['points']

        cache = {
            "statusCode": 200,
            "body": json.dumps(users, default=int),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
        cache_time = time.time()
        return cache
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json.dumps({"message": str(error), "err": "internalError"}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
