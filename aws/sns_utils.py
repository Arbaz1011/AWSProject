import boto3

def send_notification(topic_arn, message, subject):
    try:
        client = boto3.client('sns')
        response = client.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject=subject
        )
        print(f"Successfully sent SNS notification: {response['MessageId']}")
        return response
    except Exception as e:
        print(f"Error sending SNS notification: {str(e)}")
        raise e

def subscribe_email(topic_arn, email):
    try:
        client = boto3.client('sns')
        response = client.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email
        )
        return response
    except Exception as e:
        print(f"Error subscribing to SNS topic: {str(e)}")
        raise e

def unsubscribe_email(subscription_arn):
    try:
        client = boto3.client('sns')
        response = client.unsubscribe(
            SubscriptionArn=subscription_arn
        )
        return response
    except Exception as e:
        print(f"Error unsubscribing from SNS topic: {str(e)}")
        raise e
