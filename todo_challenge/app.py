import boto3
from os import environ as os_environ
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
                'body': json_dumps({"message": 'You must be a player to mark a challenge as todo', "err": "unauthorized"})
            }

        dynamodb = boto3.resource('dynamodb')

        user_table = dynamodb.Table(os_environ['USER_TABLE'])
        user = user_table.get_item(Key={'username': token['cognito:username']})['Item']

        # Get challenge
        challenge_table = dynamodb.Table(os_environ['CHALLENGES_TABLE'])
        response = challenge_table.get_item(Key={'challenge': event['pathParameters']['challenge']})

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 404,
                'body': json_dumps({"message": 'Error connecting to database', "err": "dynamodbError"})
            }

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json_dumps({"message": 'Challenge not found', "err": "notFound"})
            }

        challenge = response['Item']

        user_table.update_item(
            Key={
                'username': user['username']
            },
            UpdateExpression='SET challenges_to_do = list_append(challenges_to_do, :challenge)',
            ExpressionAttributeValues={
                ':challenge': [challenge['challenge']]
            }
        )

        return {
            'statusCode': 200,
            'body': json_dumps({"message": 'Challenge added to todo list'})
        }

    except Exception as error:
        return {
            "statusCode": 500,
            "body": json_dumps({"message": str(error), "err": "internalError"})
        }
