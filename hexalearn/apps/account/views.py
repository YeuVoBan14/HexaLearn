from rest_framework import generics, permissions

from .docs import upload_credential_schema
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

import hashlib
import time
import uuid
import boto3
import cloudinary

from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
@upload_credential_schema()
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_upload_credential(request):
    file_name = request.query_params.get('file_name', 'image')
    file_type = request.query_params.get('file_type', 'image/jpeg')
    storage_backend = settings.STORAGES['default']['BACKEND']

    if 'cloudinary' in storage_backend:
        # Dev → Cloudinary signed upload
        timestamp = int(time.time())
        folder = "flashcard"
        params = f"folder={folder}&timestamp={timestamp}{cloudinary.config().api_secret}"
        signature = hashlib.sha1(params.encode()).hexdigest()
        return Response({
            "provider": "cloudinary",
            "signature": signature,
            "timestamp": timestamp,
            "folder": folder,
            "cloud_name": cloudinary.config().cloud_name,
            "api_key": cloudinary.config().api_key,
        })

    else:
        # Prod → AWS S3 presigned URL
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        key = f"flashcard/{uuid.uuid4()}_{file_name}"
        presigned_url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': key,
                'ContentType': file_type,
            },
            ExpiresIn=300  # hết hạn sau 5 phút
        )
        file_url = (
            f"https://{settings.AWS_STORAGE_BUCKET_NAME}"
            f".s3.{settings.AWS_S3_REGION_NAME}"
            f".amazonaws.com/{key}"
        )
        return Response({
            "provider": "s3",
            "presigned_url": presigned_url,
            "file_url": file_url,
        })
