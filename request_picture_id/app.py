import random
import boto3
import json
import os

letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def lambda_handler(event, context):
    try:
        s3 = boto3.client('s3')
        bucket = os.environ['PICTURE_BUCKET']

        body = json.loads(event['body'])

        id = [letters[random.randint(0, len(letters) - 1)] for i in range(10)]

        if body['usage'] == "profile":
            fullpath = "unprocessedprofile/" + "".join(id)
        elif body['usage'] == "challenge":
            fullpath = "unprocessedchallenge/" + "".join(id)
        elif body['usage'] == "banner":
            fullpath = "unprocessedbanner/" + "".join(id)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": "Invalid usage", "err": "invalidUsage"}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        response = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': bucket,
                'Key': fullpath,
                'ContentType': 'text/plain'
            },
            HttpMethod="PUT"
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"url": response, "id": "".join(id)}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json.dumps({"message": str(error), "err": "internalError"}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
