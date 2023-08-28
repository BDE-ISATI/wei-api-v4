import boto3
import json
import os
import time
from urllib import parse

cache = {}
cache_time = {}


def lambda_handler(event, context):
    global cache
    global cache_time

    user_name = parse.unquote(event['pathParameters']['username'])
    if not (event['queryStringParameters'] and 'force_refresh' in event['queryStringParameters']) and (
            user_name in cache and time.time() < cache_time[user_name] + int(os.environ['CACHE_TIME'])):
        return cache[user_name]

    try:
        dynamodb = boto3.resource('dynamodb')
        user_table = dynamodb.Table(os.environ['USER_TABLE'])
        user = user_table.get_item(Key={'username': user_name})
        if user['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error retrieving user', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }
        if 'Item' not in user:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": "User not found", "err": "notFound"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }
        user = user['Item']

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

        user['points'] = 0
        for challenge_id in user['challenges_done']:
            # Filter to get the correct challenge
            t = list(filter(lambda x: x['challenge'] == challenge_id, challenges))
            if len(t) == 0:
                continue
            challenge = t[0]
            user['points'] += challenge['points']

        cache[user_name] = {
            "statusCode": 200,
            "body": json.dumps(user, default=int)
        }
        cache_time[user_name] = time.time()
        return cache[user_name]
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error), "err": "internalError"}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
