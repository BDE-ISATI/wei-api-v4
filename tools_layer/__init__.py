import jwt, boto3, os, time

class Token:
    def __init__(self, token: str):
        self.token = token
        self.decode_success = False

    def decode(self):
        self.decoded = jwt.decode(self.token, algorithms=['RS256'], options={"verify_signature": False})
        self.decode_success = True

    def is_valid(self):
        return self.decode_success and time.time() < self.decoded['exp']