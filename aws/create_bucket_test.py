import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()

# Get region from environment variable
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

def create_test_bucket():
    try:
        # Initialize the S3 client
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        
        # Get the current region
        session = boto3.session.Session()
        current_region = session.region_name
        
        # Try to create a bucket
        bucket_name = f'autocare-images-testing'  # e.g., autocare-images-12345
        
        print(f"Current AWS Region: {current_region}")
        print(f"Attempting to create bucket: {bucket_name}")
        
        if current_region == 'us-east-1':
            # For us-east-1, don't specify LocationConstraint
            response = s3_client.create_bucket(
                Bucket=bucket_name
            )
        else:
            # For all other regions, must specify LocationConstraint
            response = s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': current_region
                }
            )
        
        print(f"Success! Bucket created: {response}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        print("\nError creating bucket!")
        print(f"Error Code: {error_code}")
        print(f"Error Message: {error_message}")
        
        if error_code == 'BucketAlreadyExists':
            print("\nThis bucket name is already taken. Try a different name.")
        elif error_code == 'AccessDenied':
            print("\nAccess Denied. Please check:")
            print("1. Your IAM user has AmazonS3FullAccess policy")
            print("2. Your AWS credentials are correct")
        elif error_code == 'IllegalLocationConstraintException':
            print("\nRegion configuration issue. Please run:")
            print("aws configure")
            print("And make sure to set the correct region (e.g., us-east-1, ap-south-1, etc.)")
        
        return False
        
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== S3 Bucket Creation Test ===")
    print(f"Using AWS Region: {AWS_REGION}")
    success = create_test_bucket()
    if success:
        print("\n✓ Bucket creation successful!")
    else:
        print("\n❌ Bucket creation failed!")
