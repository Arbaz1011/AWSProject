import boto3

def send_notification(topic_arn, message, subject):
    client = boto3.client('sns')

    response = client.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject=subject
    )
    return response
