import boto3
from os import environ as os_environ
from json import dumps as json_dumps

def lambda_handler(event, context):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os_environ['CHALLENGES_TABLE'])

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
            "body": json_dumps(response['Items'], default=int)
        }
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json_dumps({"message": str(error), "err": "internalError"})
        }
