import boto3
from os import environ as os_environ
from jwt import decode
from json import dumps as json_dumps


def lambda_handler(event, context):
    try:
        token = decode(event['headers']['Authorization'].replace('Bearer ', ''), algorithms=['RS256'],
                           options={"verify_signature": False})

        dynamodb = boto3.resource('dynamodb')

        if 'cognito:groups' in token and 'Admin' in token['cognito:groups']:
            return {
                'statusCode': 401,
                'body': json_dumps({"message": 'You must be a player to join a team', "err": "unauthorized"})
            }

        teams_table = dynamodb.Table(os_environ['TEAMS_TABLE'])

        response = teams_table.scan(
            FilterExpression='contains(members, :player) OR contains(pending, :player)',
            ExpressionAttributeValues={
                ':player': token['cognito:username']
            }
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving teams', "err": "dynamodbError"})
            }

        if len(response['Items']) == 0:
            return {
                'statusCode': 400,
                'body': json_dumps({"message": 'You are not in a team.', "err": "notInTeam"})
            }

        team_name = response['Items'][0]['team']

        # If player is in pending
        if token['cognito:username'] in response['Items'][0]['pending']:
            index = response['Items'][0]['pending'].index(token['cognito:username'])
            response = teams_table.update_item(
                Key={
                    'team': team_name
                },
                UpdateExpression='REMOVE pending[' + str(index) + ']',
                ConditionExpression=('team = :team'),
                ExpressionAttributeValues={
                    ':team': team_name
                },
                ReturnValues="UPDATED_NEW"
            )
        else:
            index = response['Items'][0]['members'].index(token['cognito:username'])
            response = teams_table.update_item(
                Key={
                    'team': team_name
                },
                UpdateExpression='REMOVE members[' + str(index) + ']',
                ConditionExpression=('team = :team'),
                ExpressionAttributeValues={
                    ':team': team_name
                },
                ReturnValues="UPDATED_NEW"
            )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error updating team', "err": "dynamodbError"})
            }

        return {
            'statusCode': 200,
            'body': json_dumps({"message": 'Team left successfully'})
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json_dumps({"message": str(error), "err": "internalError"})
        }
