import boto3
from json import dumps as json_dumps
from os import environ as os_environ
from time import time

cache = {}
cache_time = {}


def lambda_handler(event, context):
    global cache
    global cache_time

    team_name = event['pathParameters']['team']
    if not (event['queryStringParameters'] and 'force_refresh' in event['queryStringParameters']) and (
            team_name in cache and time() < cache_time[team_name] + int(os_environ['CACHE_TIME'])):
        return cache[team_name]

    try:
        dynamodb = boto3.resource('dynamodb')

        team_table = dynamodb.Table(os_environ['TEAMS_TABLE'])
        team = team_table.get_item(Key={'team': team_name})
        if team['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving team', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }
        if 'Item' not in team:
            return {
                "statusCode": 404,
                "body": json_dumps({"message": "Team not found", "err": "notFound"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }
        team = team['Item']

        user_table = dynamodb.Table(os_environ['USER_TABLE'])
        users = user_table.scan()
        if users['ResponseMetadata']['HTTPStatusCode'] != 200 or 'Items' not in users:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving users', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }
        users = users['Items']

        challenge_table = dynamodb.Table(os_environ['CHALLENGES_TABLE'])
        challenges = challenge_table.scan()
        if challenges['ResponseMetadata']['HTTPStatusCode'] != 200 or 'Items' not in challenges:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving challenges', 'err': 'dynamodbError'}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }
        challenges = challenges['Items']

        team['points'] = 0
        members = []
        for user_id in team['members']:
            user = list(filter(lambda x: x['username'] == user_id, users))[0]
            user['points'] = 0
            for challenge_id in user['challenges_done']:
                t = list(filter(lambda x: x['challenge'] == challenge_id, challenges))
                if len(t) == 0:
                    continue
                challenge = t[0]
                user['points'] += challenge['points']
            team['points'] += user['points']
            members.append(
                {'username': user['username'], "display_name": user['display_name'], 'points': user['points'],
                 'picture_id': user['picture_id']})
            team['members'] = members

        cache[team_name] = {
            "statusCode": 200,
            "body": json_dumps(team, default=int),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
        cache_time[team_name] = time()
        return cache[team_name]
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json_dumps({"message": str(error), "err": "internalError"}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
