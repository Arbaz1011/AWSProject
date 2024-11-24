import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()

def test_image_upload():
    print("=== Testing S3 Image Upload ===")
    
    # Initialize S3 client
    s3_client = boto3.client('s3')
    bucket_name = 'autocare-images-testing'
    
    # Test image path (replace with your actual test image)
    test_image_path = 'test_images/banner.jpeg'
    
    try:
        # Create test_images directory if it doesn't exist
        if not os.path.exists('test_images'):
            os.makedirs('test_images')
        
        # First verify the bucket exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✓ Bucket '{bucket_name}' exists")
        except ClientError:
            print(f"❌ Bucket '{bucket_name}' not found!")
            return False
        
        # Upload the image
        print(f"\nUploading image: {test_image_path}")
        s3_client.upload_file(test_image_path, bucket_name, 'banner.jpeg')
        print("✓ Upload successful!")
        
        # Verify the upload by listing objects
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            print("\nFiles in bucket:")
            for obj in response['Contents']:
                print(f"- {obj['Key']} ({obj['Size']} bytes)")
        
        return True
        
    except FileNotFoundError:
        print(f"\n❌ Test image not found at: {test_image_path}")
        print("Please add a test image to the test_images directory")
        return False
    except ClientError as e:
        error = e.response.get('Error', {})
        print(f"\n❌ AWS Error: {error.get('Message', 'Unknown error')}")
        return False

if __name__ == "__main__":
    print("\n=== Testing S3 Image Upload ===")
    success = test_image_upload()
    if success:
        print("\n✓ Image upload successful!")
    else:
        print("\n❌ Image upload failed!")