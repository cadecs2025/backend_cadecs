import mimetypes
import boto3
import os


class FileUpload:

    def s3_file_upload(self,file_path):       
        

        print(f"AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID')}",flush=True)
        print(f"AWS_SECRET_ACCESS_KEY: {os.getenv('AWS_SECRET_ACCESS_KEY')}",flush=True)
        print(f"AWS_S3_REGION_NAME: {os.getenv('AWS_S3_REGION_NAME')}",flush=True)


        s3 = boto3.client('s3', 
                        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                        aws_secret_access_key= os.getenv('AWS_SECRET_ACCESS_KEY'),
                        region_name=os.getenv('AWS_S3_REGION_NAME')
                        ) 
        bucket_name = os.getenv('AWS_STORAGE_BUCKET_MEDIA_NAME', 'cadecs-media-bucket')
        s3_key = str(file_path) #f'media/images/'
        print(f"s3_key:{s3_key}",flush=True)

        file_path = str(file_path)

        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type #or 'application/octet-stream'  # Fallback to binary

        try:
            s3.upload_file(file_path, bucket_name, s3_key,ExtraArgs={
                    'ContentType': content_type,
                    'ContentDisposition': 'inline'
                })

            print("uploaded successfully",flush=True) 

            return True
        except Exception as ex:
            print(f"exceptiona: {ex}",flush=True)
            return False