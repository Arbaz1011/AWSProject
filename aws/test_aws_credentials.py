import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
load_dotenv()

# AWS Configuration
REGION = os.getenv('AWS_REGION', '')
# USER_POOL_ID = os.getenv('USER_POOL_ID')
# CLIENT_ID = os.getenv('CLIENT_ID', '850995543690')
BUCKET_NAME = os.getenv('BUCKET_NAME', '')
# SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')
# APPOINTMENTS_TABLE = os.getenv('APPOINTMENTS_TABLE')

def test_aws_setup():
    print("Testing AWS Credentials and Permissions...")
    
    try:
        # 1. Test if credentials are configured
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials is None:
            print("❌ No AWS credentials found!")
            print("Please run 'aws configure' again and ensure you enter the correct:")
            print("- AWS Access Key ID")
            print("- AWS Secret Access Key")
            print("- Default region name (e.g., us-east-1)")
            return False
            
        # 2. Print current configuration
        print("\nCurrent AWS Configuration:")
        print(f"Region: {session.region_name}")
        
        # 3. Test S3 access
        print("\nTesting S3 Access...")
        s3 = session.client('s3')
        
        # Try to list buckets (this requires minimal permissions)
        s3.list_buckets()
        print("✓ Successfully connected to AWS S3!")
        print("✓ Credentials are valid!")
        print("✓ Basic S3 permissions are working!")
        
        # Add environment variable check
        print("\nChecking Environment Variables:")
        print(f"AWS_REGION: {os.getenv('AWS_REGION', 'Not set')}")
        print(f"BUCKET_NAME: {os.getenv('BUCKET_NAME', 'Not set')}")
        # print(f"USER_POOL_ID: {os.getenv('USER_POOL_ID', 'Not set')}")
        # print(f"CLIENT_ID: {os.getenv('CLIENT_ID', 'Not set')}\n")
        
        return True
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        error_message = e.response.get('Error', {}).get('Message', '')
        
        print("\n❌ AWS Error Detected!")
        print(f"Error Code: {error_code}")
        print(f"Error Message: {error_message}")
        
        if error_code == 'InvalidAccessKeyId':
            print("\nThe AWS Access Key ID you provided is not valid.")
            print("Please check:")
            print("1. Run 'aws configure' again")
            print("2. Make sure you're copying the Access Key ID correctly")
        elif error_code == 'SignatureDoesNotMatch':
            print("\nThe AWS Secret Access Key you provided is not valid.")
            print("Please check:")
            print("1. Run 'aws configure' again")
            print("2. Make sure you're copying the Secret Access Key correctly")
        elif error_code == 'AccessDenied':
            print("\nYour credentials are valid but you don't have the required permissions.")
            print("Please check:")
            print("1. Go to AWS Console → IAM → Users → user1")
            print("2. Click 'Add permissions'")
            print("3. Choose 'Attach policies directly'")
            print("4. Search and select 'AmazonS3FullAccess'")
            print("5. Click 'Next' and 'Add permissions'")
        
        return False
        
    except Exception as e:
        print("\n❌ Unexpected Error!")
        print(f"Error: {str(e)}")
        print("\nPlease verify:")
        print("1. You have internet connection")
        print("2. AWS credentials are configured ('aws configure')")
        print("3. You're using the correct region")
        return False

if __name__ == "__main__":
    test_aws_setup()
