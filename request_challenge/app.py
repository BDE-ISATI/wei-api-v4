import os, boto3
from time import time
from jwt import decode
from json import dumps as json_dumps


def lambda_handler(event, context):
    try:
        token = decode(event['headers']['Authorization'].replace('Bearer ', ''), algorithms=['RS256'],
                           options={"verify_signature": False})

        if 'cognito:groups' in token and 'Admin' in token['cognito:groups']:
            return {
                'statusCode': 401,
                'body': json_dumps({"message": 'You must be a player to request a challenge'})
            }

        dynamodb = boto3.resource('dynamodb')

        user_table = dynamodb.Table(os.environ['USER_TABLE'])
        user = user_table.get_item(Key={'username': token['cognito:username']})['Item']

        # Get challenge
        challenge_table = dynamodb.Table(os.environ['CHALLENGES_TABLE'])
        response = challenge_table.get_item(Key={'challenge': event['pathParameters']['challenge']})

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 404,
                'body': json_dumps({"message": 'Error connecting to database'})
            }

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json_dumps({"message": 'Challenge not found'})
            }

        challenge = response['Item']

        if not challenge:
            return {
                'statusCode': 404,
                'body': json_dumps({"message": 'Challenge not found'})
            }

        if user['challenges_done'].count(challenge['challenge']) + user['challenges_pending'].count(challenge['challenge']) >= challenge['max_count']:
            return {
                'statusCode': 400,
                'body': json_dumps({"message": 'You have already completed this challenge the maximum number of times'})
            }

        t = int(time())
        print(f'Time : {t}')
        if challenge['start'] > t or challenge['end'] < t:
            return {
                'statusCode': 400,
                'body': json_dumps({"message": 'Challenge not active'})
            }

        # Add the challenge to the user's pending challenges
        user_table.update_item(
            Key={
                'username': user['username']
            },
            UpdateExpression='SET challenges_pending = list_append(challenges_pending, :challenge)',
            ExpressionAttributeValues={
                ':challenge': [challenge['challenge']]
            }
        )

        return {
            'statusCode': 200,
            'body': json_dumps({"message": 'Challenge requested'})
        }

    except Exception as error:
        return {
            "statusCode": 500,
            "body": json_dumps({"message": str(error)})
        }
