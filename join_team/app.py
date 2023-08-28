import boto3
import json
import os
import jwt
from urllib import parse

def lambda_handler(event, context):
    try:
        token = jwt.decode(event['headers']['Authorization'].replace('Bearer ', ''), algorithms=['RS256'],
                       options={"verify_signature": False})

        dynamodb = boto3.resource('dynamodb')

        if 'cognito:groups' in token and 'Admin' in token['cognito:groups']:
            return {
                'statusCode': 401,
                'body': json.dumps({"message": 'You must be a player to join a team', "err": "unauthorized"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        teams_table = dynamodb.Table(os.environ['TEAMS_TABLE'])
        team_name = parse.unquote(event['pathParameters']['team'])

        # Check if player is already in a team
        response = teams_table.scan(
            FilterExpression='contains(members, :player) OR contains(pending, :player)',
            ExpressionAttributeValues={
                ':player': token['cognito:username']
            }
        )
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error retrieving teams', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }
        if len(response['Items']) > 0:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'You are already in a team.', "err": "alreadyInTeam"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        response = teams_table.update_item(
            Key={
                'team': team_name
            },
            UpdateExpression='SET pending = list_append(pending, :player)',
            ConditionExpression=('team = :team'),
            ExpressionAttributeValues={
                ':player': [token['cognito:username']],
                ':team': team_name
            },
            ReturnValues="UPDATED_NEW"
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error updating team', "err": "dynamodbError"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        return {
            'statusCode': 200,
            'body': json.dumps({"message": 'Team joined successfully'}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error), "err": "internalError"}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
