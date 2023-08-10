import boto3
from os import environ as os_environ
from json import dumps as json_dumps

def lambda_handler(event, context):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os_environ['CHALLENGES_TABLE'])

        # Get user from event.pathParameters.username
        response = table.get_item(
            Key={
                'challenge': event['pathParameters']['challenge']
            }
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json_dumps({"message": 'Error retrieving challenge', "err": "dynamodbError"})
            }

        # Create response, if empty return 404
        if 'Item' not in response:
            return {
                "statusCode": 404,
                "body": json_dumps({"message": "Challenge not found", "err": "notFound"})
            }

        return {
            "statusCode": 200,
            "body": json_dumps(response['Item'], default=int)
        }
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json_dumps({"message": str(error), "err": "internalError"})
        }
