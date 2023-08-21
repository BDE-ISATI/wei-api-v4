import random

import boto3
from os import environ as os_environ
from json import dumps as json_dumps
from json import loads as json_loads

letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def lambda_handler(event, context):
    try:
        s3 = boto3.client('s3')
        bucket = os_environ['PICTURE_BUCKET']

        body = json_loads(event['body'])

        id = [letters[random.randint(0, len(letters) - 1)] for i in range(10)]

        if body['usage'] == "profile":
            fullpath = "unprocessedprofile/" + "".join(id)
        elif body['usage'] == "challenge":
            fullpath = "unprocessedchallenge/" + "".join(id)
        else:
            return {
                'statusCode': 400,
                'body': json_dumps({"message": "Invalid usage", "err": "invalidUsage"})
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
            "body": json_dumps({"url": response, "id": "".join(id)})
        }
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json_dumps({"message": str(error), "err": "internalError"})
        }
