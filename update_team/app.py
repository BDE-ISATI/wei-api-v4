import boto3
from jwt import decode
from json import loads as json_loads
from json import dumps as json_dumps
from os import environ as os_environ


def lambda_handler(event, context):
    try:
        token = decode(event['headers']['Authorization'].replace('Bearer ', ''), algorithms=['RS256'],
                           options={"verify_signature": False})

        if 'cognito:groups' not in token or 'Admin' not in token['cognito:groups']:
            return {
                'statusCode': 401,
                'body': json_dumps({"message": 'Unauthorized', "err": "unauthorized"})
            }

        body = json_loads(event['body'])

        if 'display_name' not in body and 'picture_id' not in body:
            return {
                'statusCode': 400,
                'body': json_dumps({"message": 'Missing body', "err": "emptyBody"})
            }

        dynamodb = boto3.resource('dynamodb')

        teams_table = dynamodb.Table(os_environ['TEAMS_TABLE'])
        team_name = event['pathParameters']['team']

        display_name = body['display_name'] if 'display_name' in body else ''
        picture_id = body['picture_id'] if 'picture_id' in body else ''

        update_values = {}
        update_expression = "set "
        if display_name != '':
            update_expression += "display_name=:d"
            update_values[':d'] = display_name

        if picture_id != '':
            if len(update_values) > 0:
                update_expression += ", "
            update_expression += "picture_id=:p"
            update_values[':p'] = picture_id

        update_values[':t'] = team_name
        response = teams_table.update_item(
            Key={
                'team': team_name
            },
            UpdateExpression=update_expression,
            ConditionExpression="team=:t",
            ExpressionAttributeValues=update_values,
            ReturnValues="UPDATED_NEW"
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error updating team', "err": "dynamodbError"})
            }

        return {
            'statusCode': 200,
            'body': json_dumps({"message": 'Team updated successfully'})
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json_dumps({"message": str(error), "err": "internalError"})
        }
