import boto3
from json import dumps as json_dumps
from os import environ as os_environ


def lambda_handler(event, context):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os_environ['TEAMS_TABLE'])

        # Get all users
        response = table.scan()

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving challenges', "err": "dynamodbError"})
            }

        # Create response
        return {
            "statusCode": 200,
            "body": json_dumps(response['Items'])
        }
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json_dumps({"message": str(error), "err": "internalError"})
        }
