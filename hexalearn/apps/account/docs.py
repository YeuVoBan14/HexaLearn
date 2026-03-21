from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers

def upload_credential_schema():
    return extend_schema(
        summary="Get upload credential",
        responses={
            200: inline_serializer(
                name='UploadCredentialResponse',
                fields={
                    'provider': serializers.CharField(),
                    'signature': serializers.CharField(required=False),
                    'timestamp': serializers.IntegerField(required=False),
                    'folder': serializers.CharField(required=False),
                    'cloud_name': serializers.CharField(required=False),
                    'api_key': serializers.CharField(required=False),
                    'presigned_url': serializers.CharField(required=False),
                    'file_url': serializers.CharField(required=False),
                }
            ),
            401: OpenApiResponse(description="Not logged in or invalid token."),
        },
    )