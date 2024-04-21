from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from api.v1.shema import (
    USER_CREATE_EXAMPLE,
    USER_CREATED_201,
    USER_BAD_REQUEST_400,
)
from users.serializers import (
    UserCreateSerializer,
)

User = get_user_model()


@extend_schema(
    request=UserCreateSerializer,
    summary="Регистрация пользователя",
    tags=["Users"],
    examples=[USER_CREATE_EXAMPLE],
    responses={
        status.HTTP_201_CREATED: USER_CREATED_201,
        status.HTTP_400_BAD_REQUEST: USER_BAD_REQUEST_400,
    },
)
class RegisrtyView(GenericAPIView):
    """
    Регистрация пользователей.
    """

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
