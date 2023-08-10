import boto3
from json import dumps as json_dumps
from os import environ as os_environ

def lambda_handler(event, context):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os_environ['TEAMS_TABLE'])

        # Get user from event.pathParameters.username
        response = table.get_item(
            Key={
                'team': event['pathParameters']['team']
            }
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Eror retrieving team', "err": "dynamodbError"})
            }

        # Create response, if empty return 404
        if 'Item' not in response:
            return {
                "statusCode": 404,
                "body": json_dumps({"message": "Team not found", "err": "notFound"})
            }

        return {
            "statusCode": 200,
            "body": json_dumps(response['Item'])
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json_dumps({"message": str(error), "err": "internalError"})
        }

