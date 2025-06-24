import os
import boto3
from botocore.exceptions import ClientError

class S3Wrapper:
    def __init__(self, bucket_name, profile_name='personal', region = 'us-east-2'):
        self.bucket_name = bucket_name
        self.region = region
        self.session = boto3.Session(profile_name=profile_name)
        self.s3_client = self.session.client('s3')

    def list_directory(self, prefix=''):
        """List objects in a directory (prefix)"""
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            return [content['Key'] for content in response.get('Contents', [])]
        except ClientError as e:
            print(f"Error listing directory: {e}")
            return []

    def create_folder(self, folder_name):
        """Create a folder by uploading an empty object with a trailing slash"""
        if not folder_name.endswith('/'):
            folder_name += '/'
        # Check if folder already exists
        existing_objects = self.list_directory(prefix=folder_name)
        if existing_objects:
            print(f"Folder '{folder_name}' already exists.")
            return
        try:
            self.s3_client.put_object(Bucket=self.bucket_name, Key=folder_name)
            print(f"Folder '{folder_name}' created successfully.")
        except ClientError as e:
            print(f"Error creating folder: {e}")

    def upload_file(self, file_path, s3_key):

        """Upload a file to S3"""

        s3_key = s3_key.replace('\\', '/') # s3 why you do this???

        extra_args = {}
        if file_path.lower().endswith('.pdf'):
            extra_args = {
                'ContentType': 'application/pdf',
            }

        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key, ExtraArgs=extra_args)
            print(f"File '{file_path}' uploaded to '{s3_key}' successfully.")

            return os.path.join(f'https://{self.bucket_name}.s3.{self.region}.amazonaws.com/', s3_key).replace('\\', '/')
        except ClientError as e:
            print(f"Error uploading file: {e}")

    def delete_folder(self, folder_name):
        """Delete a folder by removing all objects within it"""
        if not folder_name.endswith('/'):
            folder_name += '/'
        try:
            objects = self.list_directory(prefix=folder_name)
            if objects:
                delete_objects = {'Objects': [{'Key': obj} for obj in objects]}
                self.s3_client.delete_objects(Bucket=self.bucket_name, Delete=delete_objects)
                print(f"Folder '{folder_name}' and its contents deleted successfully.")
            else:
                print(f"Folder '{folder_name}' is empty or does not exist.")
        except ClientError as e:
            print(f"Error deleting folder: {e}")

    def delete_file(self, file_key):
        """Delete a file from S3"""

        file_key = file_key.replace('\\', '/') # s3 why you do this???

        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            print(f"File '{file_key}' deleted successfully.")
        except ClientError as e:
            print(f"Error deleting file: {e}")

    def download_file(self, s3_key, local_path):
        """Download a file from S3 to a specified local path"""

        s3_key = s3_key.replace('\\', '/') # s3 why you do this???

        end_location = os.path.dirname(local_path)

        os.makedirs(end_location, exist_ok = True)

        try:
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            print(f"File '{s3_key}' downloaded to '{local_path}' successfully.")
        except ClientError as e:
            print(f"Error downloading file: {e}")
    
    def download_url_to_directory(self, url: str, directory: str):
        """Download a s3 url to a specified path. Does not change file name"""

        file_path = url.partition('amazonaws.com/')[2]

        file_name = os.path.basename(url)

        to_file = os.path.join(directory, file_name)

        self.download_file(file_path, to_file)

# Example usage
if __name__ == "__main__":
    bucket_name = "logan-public-files"
    s3_wrapper = S3Wrapper(bucket_name)

    # List directory
    print(s3_wrapper.list_directory("projects"))

    # # Create folder
    # s3_wrapper.create_folder("example-folder")

    # # Upload file
    # s3_wrapper.upload_file("local_file.txt", "example-folder/local_file.txt")

    # # Delete file
    # s3_wrapper.delete_file("example-folder/local_file.txt")

    # # Delete folder
    # s3_wrapper.delete_folder("example-folder")
