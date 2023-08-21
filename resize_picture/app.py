import boto3
from PIL import Image
from io import BytesIO
from json import dumps as json_dumps

client = boto3.client('s3')

def lambda_handler(event, context):
    bucket_arn = event['Records'][0]['s3']['bucket']['arn']
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    image_name = event['Records'][0]['s3']['object']['key']
    print(bucket_arn)
    print(bucket_name)
    print(image_name)

    file_byte_string = client.get_object(Bucket=bucket_name, Key=image_name)['Body'].read()

    img = Image.open(BytesIO(file_byte_string))

    if "profile" in image_name:
        img = img.resize((128, 128))

    buffer = BytesIO()
    img.save(buffer, "PNG")
    buffer.seek(0)
    sent_data = client.put_object(Bucket=bucket_name, Key=image_name.split('/')[1] + ".png", Body=buffer)
    if sent_data['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise RuntimeError('Failed to upload image {} to bucket {}'.format(image_name, bucket_name))

    client.delete_object(Bucket=bucket_name, Key=image_name)

    return {
        'statusCode': 200,
        'body': json_dumps('Image processed')
    }

