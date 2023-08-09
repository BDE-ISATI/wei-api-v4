import json, boto3, os
# import requests


def lambda_handler(event, context):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['USER_TABLE'])

        # Get username from event.pathParameters.username
        # Create user
        response = table.put_item(
            Item={
                'username': event['userName'],
                'mail': event['request']['userAttributes']['email'],
                'challenges_done': [],
                'challenges_pending': [],
                'challenges_to_do': [],
                'profile_picture_id': '',
                'show': True,
            }
        )

        # Check if creation was successful
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            print('Error creating user')
    except:
        pass

    return event
    # return {
    #     "statusCode": 200,
    #     "body": json.dumps({
    #         "message": "You are not supposed to be here!",
    #         # "location": ip.text.replace("\n", "")
    #     }),
    # }
