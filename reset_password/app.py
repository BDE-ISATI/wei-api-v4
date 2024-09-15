import boto3
import json

def lambda_handler(event, context):
    try:
        client = boto3.client('cognito-idp')

        body = json.loads(event['body'])

        response = client.confirm_forgot_password(
            ClientId='6b2qoi7siljqa47u59lmand95q',
            Username=body["username"],
            ConfirmationCode=body["code"],
            Password=body["password"],
        )

        return {
            'statusCode': 200,
            'body': json.dumps({"message": 'Challenge removed from todo'}),
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
