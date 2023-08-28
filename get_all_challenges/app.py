import boto3
import json
import os
import time

cache = None
cache_time = 0


def format_user(user, challenge_id):
    v = {"username": user['username'], 'display_name': user['display_name'],
         "picture_id": user["picture_id"] if 'picture_id' in user else '', 'time': -1}

    if 'challenges_times' in user and challenge_id in user['challenges_times']:
        v['time'] = user['challenges_times'][challenge_id]

    return v


def lambda_handler(event, context):
    global cache
    global cache_time

    if not (event['queryStringParameters'] and 'force_refresh' in event['queryStringParameters']) and (
            cache is not None and time.time() < cache_time + int(os.environ['CACHE_TIME'])):
        return cache

    try:
        dynamodb = boto3.resource('dynamodb')
        challenge_table = dynamodb.Table(os.environ['CHALLENGES_TABLE'])
        user_table = dynamodb.Table(os.environ['USER_TABLE'])

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

        for challenge in challenges:
            t = list(filter(lambda x: challenge['challenge'] in x['challenges_done'], users))
            challenge['users'] = [format_user(x, challenge['challenge']) for x in t]

        cache = {
            "statusCode": 200,
            "body": json.dumps(challenges, default=int),
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
