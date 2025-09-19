from rest_framework import serializers

from api.v1.serializers.image_fields import Base64ImageField
from api.v1.serializers.users_serializers import UserReadSerializer
from api.v1.validators import (
    validate_base64_field,
    validate_extention,
    validate_file_quantity,
    validate_file_size,
)
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

    def validate_image(self, value):
        validate_base64_field(value)
        return value


class CommentImageRetrieveSerializer(CommentImageCreateSerializer):
    """Сериализатор для получения фото комментариев."""

    class Meta(CommentImageCreateSerializer.Meta):
        fields = CommentImageCreateSerializer.Meta.fields + ("id",)  # type: ignore  # noqa


class CommentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания комментария."""

    images = CommentImageAddSerializer(many=True, required=False)

    class Meta:
        model = Comment
        fields = ("rating", "feedback", "images")

    def create(self, validated_data):
        if "images" not in validated_data.keys():
            comment = Comment.objects.create(**validated_data)
            return comment
        images = validated_data.pop("images")
        comment = Comment.objects.create(**validated_data)
        for image in images:
            img_serializer = CommentImageCreateSerializer(data=image)
            if img_serializer.is_valid(raise_exception=True):
                img_serializer.save(comment=comment)
        return comment

    def validate_images(self, data):
        validate_file_quantity(data)
        for img in data:
            validate_base64_field(img["image"])
            format, _ = img["image"].split(";base64,")
            ext = format.split("/")[-1]
            validate_extention(ext)
        return data


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
