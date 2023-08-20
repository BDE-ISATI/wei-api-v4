import boto3, os


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['USER_TABLE'])

    # Create user
    response = table.put_item(
        Item={
            'username': event['userName'],
            'display_name': event['userName'],
            'mail': event['request']['userAttributes']['email'],
            'challenges_done': [],
            'challenges_pending': [],
            'challenges_to_do': [],
            'picture_id': '',
            'show': True,
        }
    )

    return event