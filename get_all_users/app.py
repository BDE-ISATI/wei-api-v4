import boto3
from json import dumps as json_dumps
from os import environ as os_environ


def lambda_handler(event, context):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os_environ['USER_TABLE'])
        challenge_table = dynamodb.Table(os_environ['CHALLENGES_TABLE'])

        # Get all users
        users = table.scan()


        if users['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving users', "err": "dynamodbError"})
            }

        challenges = challenge_table.scan()


        if challenges['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving challenges', "err": "dynamodbError"})
            }

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
            "body": json_dumps(users['Items'], default=int)
        }
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json_dumps({"message": str(error), "err": "internalError"})
        }
