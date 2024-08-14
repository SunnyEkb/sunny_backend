from rest_framework import serializers

from api.v1.validators import validate_file_size
from comments.models import Comment, CommentImage
from users.serializers import UserReadSerializer


class CommentImageCreateSerializer(serializers.Serializer):
    """Сериализатор для создания фото к комментарию."""

    image = serializers.ImageField(
        required=True,
        allow_null=False,
        validators=[validate_file_size],
    )

    class Meta:
        model = CommentImage
        fields = ("image",)


class CommentImageRetrieveSerializer(CommentImageCreateSerializer):
    """Сериализатор для получения фото комментариев."""

    class Meta(CommentImageCreateSerializer.Meta):
        fields = CommentImageCreateSerializer.Meta.fields + ("id",)


class CommentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания комментария."""

    class Meta:
        model = Comment
        fields = (
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
