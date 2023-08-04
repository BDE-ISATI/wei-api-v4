# WEI API V2

A more secure and reliable WEI api built on AWS.

# Deploying

## Prerequisites

- [AWS CLI](https://aws.amazon.com/cli/)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)

## AWS Setup

Once you have the cli and sam installed, there is a few more step before deploying.

- You must setup a valid email in amazon SES. This is used to send emails to users for validation and password resets.
- Replace the value of `SESMailAddressArn` in `samconfig.toml` by the ARN of the email you set in the first step.
- Once done you can deploy the app using the following command: `sam deploy -t template.yaml`. You can use the `--guided` option to be guided through the deployment process.

# Reinstalling layer packages

```pip install -r requirements.txt -t python --platform manylinux2014_x86_64 --implementation cp --python-version 3.11 --only-binary=:all: --upgrade```