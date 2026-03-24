from django.shortcuts import render
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from .models import Language, Level, Source
from .serializers import LanguageSerializer, LevelSerializer, RegisterSerializer, SourceSerializer, UserProfileSerializer
from .docs import *
from .pagination import CustomPagination

# Create your views here.

@language_schema()
class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination

@level_schema()
class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination


@source_schema()
class SourceViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination


@user_profile_schema()
class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user.profile

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,           # only update fields provided in the request
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@avatar_upload_schema()
class AvatarUploadView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvatarSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user.profile

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.profile_picture:
            print("Deleting old profile picture:",
                  instance.profile_picture.url)
            instance.profile_picture.delete(save=False)

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@register_schema()
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


@delete_account_schema()
class DeleteAccountView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        profile = request.user.profile
        profile.is_deleted = True
        profile.save()
        return Response(
            {"detail": "Account has been deleted."},
            status=status.HTTP_200_OK
        )
