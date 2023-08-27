import boto3
from os import environ as os_environ
from jwt import decode
from json import dumps as json_dumps


def lambda_handler(event, context):
    try:
        token = decode(event['headers']['Authorization'].replace('Bearer ', ''), algorithms=['RS256'],
                       options={"verify_signature": False})

        if 'cognito:groups' in token and 'Admin' in token['cognito:groups']:
            return {
                'statusCode': 401,
                'body': json_dumps(
                    {"message": 'You must be a player to mark a challenge as todo', "err": "unauthorized"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        dynamodb = boto3.resource('dynamodb')

        user_table = dynamodb.Table(os_environ['USER_TABLE'])

        username = token['cognito:username']
        challenge_id = event['pathParameters']['challenge']

        user = user_table.get_item(Key={'username': username})

        if user['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error getting user', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        if 'Item' not in user:
            return {
                'statusCode': 404,
                'body': json_dumps({"message": 'User not found', "err": "notFound"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        user = user['Item']

        if challenge_id in user['challenges_to_do']:
            return {
                'statusCode': 400,
                'body': json_dumps({"message": 'Challenge already in todo', "err": "alreadyInTodo"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        # Get challenge
        challenge_table = dynamodb.Table(os_environ['CHALLENGES_TABLE'])
        challenge = challenge_table.get_item(Key={'challenge': challenge_id})

        if challenge['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 404,
                'body': json_dumps({"message": 'Error connecting to database', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        if 'Item' not in challenge:
            return {
                'statusCode': 404,
                'body': json_dumps({"message": 'Challenge not found', "err": "notFound"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        challenge = challenge['Item']

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
            'body': json_dumps({"message": 'Challenge added to todo list'}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }

    except Exception as error:
        return {
            "statusCode": 500,
            "body": json_dumps({"message": str(error), "err": "internalError"}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
