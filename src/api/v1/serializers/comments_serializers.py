from rest_framework import serializers

from api.v1.serializers.image_fields import Base64ImageField
from api.v1.serializers.users_serializers import UserReadSerializer
from api.v1.validators import validate_file_size
from comments.models import Comment, CommentImage


class CommentImageCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания фото к комментарию."""

    image = Base64ImageField(
        required=True,
        allow_null=True,
        validators=[validate_file_size],
    )

    class Meta:
        model = CommentImage
        fields = ("image",)


class CommentImageAddSerializer(serializers.Serializer):
    """Сериализатор для создания фото к комментарию."""

    image = serializers.CharField()


class CommentImageRetrieveSerializer(CommentImageCreateSerializer):
    """Сериализатор для получения фото комментариев."""

    class Meta(CommentImageCreateSerializer.Meta):
        fields = CommentImageCreateSerializer.Meta.fields + ("id",)  # type: ignore  # noqa


class CommentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания комментария."""

    images = CommentImageAddSerializer(many=True)

    class Meta:
        model = Comment
        fields = ("rating", "feedback", "images")

    def create(self, validated_data):
        images = validated_data.pop("images")
        comment = Comment.objects.create(**validated_data)
        for image in images:
            print(image)
            img_serializer = CommentImageCreateSerializer(data=image)
            print(img_serializer.is_valid())
            if img_serializer.is_valid():
                img_serializer.save(comment=comment)
        return comment


class CommentForModerationSerializer(CommentCreateSerializer):
    """Сериализатор для модерации комментариев."""

    images = CommentImageRetrieveSerializer(many=True, read_only=True)

    class Meta(CommentCreateSerializer.Meta):
        fields = CommentCreateSerializer.Meta.fields + ("id", "images")  # type: ignore  # noqa


class CommentReadSerializer(CommentForModerationSerializer):
    """Сериализатор для чтения комментария."""

    author = UserReadSerializer(read_only=True)

    class Meta(CommentForModerationSerializer.Meta):
        fields = CommentCreateSerializer.Meta.fields + ("author",)  # type: ignore  # noqa
