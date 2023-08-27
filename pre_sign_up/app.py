import re
from json import dumps as json_dumps


def lambda_handler(event, context):
    if not re.match(r'^[A-Za-z_\-0-9.]+$', event['userName']):
        raise Exception("Invalid username")

    return event
