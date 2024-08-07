from rest_framework import serializers

from comments.models import Comment, CommentImage
from services.serializers import ServiceImageCreateSerializer
from users.serializers import UserReadSerializer


class CommentImageCreateSerializer(ServiceImageCreateSerializer):
    """Сериализатор для создания фото к комментарию."""

    class Meta(ServiceImageCreateSerializer.Meta):
        model = CommentImage


class CommentImageRetrieveSerializer(CommentImageCreateSerializer):
    """Сериализатор для получения фото комментариев."""

    class Meta(CommentImageCreateSerializer.Meta):
        fields = CommentImageCreateSerializer.Meta.fields + ("id",)


class CommentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания комментария."""

    class Meta:
        model = Comment
        fields = (
            "content_type",
            "object_id",
            "rating",
            "feedback",
        )


class CommentReadSerializer(CommentCreateSerializer):
    """Сериализатор для чтения комментария."""

    author = UserReadSerializer(read_only=True)
    images = CommentImageRetrieveSerializer(many=True, read_only=True)

    class Meta(CommentCreateSerializer.Meta):
        fields = CommentCreateSerializer.Meta.fields + (
            "id",
            "author",
            "images",
        )
