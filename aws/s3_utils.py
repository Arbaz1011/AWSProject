import boto3
from botocore.exceptions import ClientError
import mimetypes
import os
import json

def get_s3_client(region=None):
    """Initialize S3 client with optional region."""
    try:
        if region is None:
            s3_client = boto3.client('s3')
        else:
            s3_client = boto3.client('s3', region_name=region)
        
        # Test credentials by making a simple API call
        s3_client.list_buckets()
        print("Successfully connected to AWS S3")
        return s3_client
    except ClientError as e:
        print(f"AWS Error: {e.response['Error']['Message']}")
        return None
    except Exception as e:
        print(f"Error initializing S3 client: {str(e)}")
        return None

def create_bucket(s3_client, bucket_name, region=None):
    """Create an S3 bucket in a specified region."""
    try:
        if region is None or region == 'us-east-1':
            # For us-east-1, don't specify LocationConstraint
            response = s3_client.create_bucket(
                Bucket=bucket_name,
                ObjectOwnership='ObjectWriter'
            )
        else:
            # For other regions, specify LocationConstraint
            response = s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': region
                },
                ObjectOwnership='ObjectWriter'
            )
            
        # Wait for bucket to exist
        waiter = s3_client.get_waiter('bucket_exists')
        waiter.wait(Bucket=bucket_name)
            
        # Set bucket public access settings
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        )
        
        # Configure bucket ownership controls
        s3_client.put_bucket_ownership_controls(
            Bucket=bucket_name,
            OwnershipControls={
                'Rules': [
                    {
                        'ObjectOwnership': 'BucketOwnerPreferred'
                    }
                ]
            }
        )
        
        # Add bucket policy to allow public read access
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{bucket_name}",
                        f"arn:aws:s3:::{bucket_name}/*"
                    ]
                }
            ]
        }
        
        # Convert the policy to JSON string
        bucket_policy = json.dumps(bucket_policy)
        
        # Put the bucket policy
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=bucket_policy
        )
        
        print(f"Successfully created bucket '{bucket_name}' in region '{region or 'us-east-1'}'")
        return bucket_name
    except ClientError as e:
        print(f"Error creating bucket: {e.response['Error']['Message']}")
        return None

def upload_car_image(s3_client, bucket_name, image_name, file_path):
    """Upload a car image to the S3 bucket."""
    if s3_client is None:
        print("Error: S3 client not initialized.")
        return False

    try:
        # Clean the file path
        clean_path = file_path.strip('"\'')
        
        # Upload the file with public-read ACL
        s3_client.upload_file(
            clean_path, 
            bucket_name, 
            image_name,
            ExtraArgs={
                'ACL': 'public-read',
                'ContentType': mimetypes.guess_type(clean_path)[0] or 'application/octet-stream'
            }
        )
        
        # Generate and return the URL
        url = f"https://{bucket_name}.s3.amazonaws.com/{image_name}"
        print(f"Successfully uploaded image. URL: {url}")
        return url
        
    except ClientError as e:
        print(f"Error uploading file: {e.response['Error']['Message']}")
        return None
    except FileNotFoundError:
        print(f"Error: File not found at path: {clean_path}")
        return None

def configure_bucket_cors(s3_client, bucket_name):
    """Configure CORS for the S3 bucket."""
    cors_configuration = {
        'CORSRules': [{
            'AllowedHeaders': ['*'],
            'AllowedMethods': ['PUT', 'POST', 'GET'],
            'AllowedOrigins': ['*'],
            'ExposeHeaders': []
        }]
    }
    
    try:
        s3_client.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration=cors_configuration
        )
        print(f"Successfully configured CORS for bucket {bucket_name}")
        return True
    except Exception as e:
        print(f"Error configuring CORS: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    # Initialize with specific region
    region = 'us-east-1'  # Default region
    s3_client = get_s3_client(region)
    
    if s3_client:
        # Create a new bucket with a unique name
        bucket_name = 'autocare-images1-test-123'  # Make sure this is unique
        bucket = create_bucket(s3_client, bucket_name)
        
        if bucket:
            # Test uploading an image
            try:
                test_image_path = 'test_images/banner.jpeg'
                if os.path.exists(test_image_path):
                    image_url = upload_car_image(
                        s3_client,
                        bucket_name,
                        'banner.jpeg',
                        test_image_path
                    )
                    if image_url:
                        print(f"Test successful! Image available at: {image_url}")
                else:
                    print(f"Test image not found at: {test_image_path}")
            except Exception as e:
                print(f"Error during testing: {str(e)}")
