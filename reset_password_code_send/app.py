import boto3
import json

def lambda_handler(event, context):
    try:
        client = boto3.client('cognito-idp')

        body = json.loads(event['body'])

        response = client.forgot_password(
            ClientId=body['ClientId'],
            Username=body["username"]
        )

        return {
            'statusCode': 200,
            'body': json.dumps({"message": 'Code sent'}),
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
