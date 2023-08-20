import boto3
from os import environ as os_environ
from jwt import decode
from json import dumps as json_dumps

def lambda_handler(event, context):
    try:
        token = decode(event['headers']['Authorization'].replace('Bearer ', ''), algorithms=['RS256'], options={"verify_signature": False})

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os_environ['USER_TABLE'])

        # Get user from event.pathParameters.username
        response = table.get_item(
            Key={
                'username': token['cognito:username']
            }
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving user', "err": "dynamodbError"})
            }

        # Create response, if empty return 404
        if 'Item' not in response:
            return {
                "statusCode": 404,
                "body": json_dumps({"message": "User not found", "err": "notFound"})
            }

        challenge_table = dynamodb.Table(os_environ['CHALLENGES_TABLE'])
        challenges = challenge_table.scan()

        response['Item']['points'] = 0
        for challenge_id in response['Item']['challenges_done']:
            # Filter to get the correct challenge
            t = list(filter(lambda x: x['challenge'] == challenge_id, challenges['Items']))
            if len(t) == 0:
                continue
            challenge = t[0]
            response['Item']['points'] += challenge['points']

        response['Item']['is_admin'] = 'cognito:groups' in token and 'Admin' in token['cognito:groups']
        return {
            "statusCode": 200,
            "body": json_dumps(response['Item'], default=int)
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json_dumps({"message": str(error), "err": "internalError"})
        }

