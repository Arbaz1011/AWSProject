import boto3
import json

def create_lambda_function(function_name, role_arn, handler, zip_file_path, runtime="python3.9"):
    """
    Create a Lambda function programmatically.
    """
    client = boto3.client('lambda')

    with open(zip_file_path, 'rb') as zip_file:
        zipped_code = zip_file.read()

    try:
        response = client.create_function(
            FunctionName=function_name,
            Runtime=runtime,
            Role=role_arn,
            Handler=handler,
            Code={'./validate_appointment.zip': './validate_appointment.py'},
            Description="Validates appointment data",
            Timeout=10,  # seconds
            MemorySize=128,
            Publish=True
        )
        return response
    except Exception as e:
        return {"Error": str(e)}

def invoke_lambda_function(function_name, payload):
    """
    Invoke a Lambda function programmatically.
    """
    client = boto3.client('lambda')

    response = client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload),
    )
    response_payload = json.loads(response['Payload'].read())
    return response_payload
