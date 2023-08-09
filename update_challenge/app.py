import boto3, json, os, jwt


def lambda_handler(event, context):
    try:
        token = jwt.decode(event['headers']['Authorization'].replace('Bearer ', ''), algorithms=['RS256'],
                           options={"verify_signature": False})

        if 'cognito:groups' not in token or 'Admin' not in token['cognito:groups']:
            return {
                'statusCode': 401,
                'body': json.dumps({"message": 'Unauthorized'})
            }

        body = json.loads(event['body'])

        if len(body) == 0:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'Missing parameters'})
            }

        dynamodb = boto3.resource('dynamodb')

        challenge_table = dynamodb.Table(os.environ['CHALLENGES_TABLE'])
        challenge_id = event['pathParameters']['challenge']

        name = body['name'] if 'name' in body else ''
        description = body['description'] if 'description' in body else ''
        picture_id = body['picture_id'] if 'picture_id' in body else ''
        points = body['points'] if 'points' in body else 0
        if points < 0:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'points must be greater than 0'})
            }

        start = body['start'] if 'start' in body else ''
        end = body['end'] if 'end' in body else ''

        max_count = body['max_count'] if 'max_count' in body else 0
        if max_count < 0:
            return {
                'statusCode': 400,
                'body': json.dumps({"message": 'max_count must be greater than 0'})
            }

        names = {}
        update_expression = "set "
        values = {}
        if name != '':
            update_expression += "#n=:n"
            names['#n'] = 'name'
            values[':n'] = name

        if description != '':
            if len(values) > 0:
                update_expression += ", "
            update_expression += "description=:d"
            values[':d'] = description

        if picture_id != '':
            if len(values) > 0:
                update_expression += ", "
            update_expression += "picture_id=:p"
            values[':p'] = picture_id

        if points != 0:
            if len(values) > 0:
                update_expression += ", "
            update_expression += "points=:p"
            values[':p'] = points

        if start != '':
            if len(values) > 0:
                update_expression += ", "
            update_expression += "start=:s"
            values[':s'] = start

        if end != '':
            if len(values) > 0:
                update_expression += ", "
            update_expression += "end=:e"
            values[':e'] = end

        if max_count != 0:
            if len(values) > 0:
                update_expression += ", "
            update_expression += "max_count=:m"
            values[':m'] = max_count

        values[':c'] = challenge_id
        response = challenge_table.update_item(
            Key={
                'challenge': challenge_id
            },
            UpdateExpression=update_expression,
            ConditionExpression="challenge = :c",
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values,
            ReturnValues="UPDATED_NEW"
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({"message": 'Error updating challenge'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({"message": 'Challenge updated successfully'})
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)})
        }
