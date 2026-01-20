import boto3
import json
from botocore.exceptions import ClientError
print(boto3.__version__)

client = boto3.client('lambda')

def lambda_handler(event, context):
    callback_id = event["callback_id"]
    status = event["status"]

    try:
        client.send_durable_execution_callback_success(
            CallbackId=callback_id,
            Result=status
        )
    except ClientError as e:
        # Notify failure
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }
    return {
        "statusCode": 200,
        "message": "Callback Sent"
    }
