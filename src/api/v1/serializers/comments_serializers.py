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
        """Настройки сериализатора."""

        model = CommentImage
        fields = ("image",)


class CommentImageAddSerializer(serializers.Serializer):
    """Сериализатор для создания фото к комментарию."""

    image = serializers.CharField()

    def validate_image(self, value: str) -> str:
        """Валидация строки в base64.

        Args:
            value (str): строка

        Returns:
            str: строка

        """
        validate_base64_field(value)
        return value


class CommentImageRetrieveSerializer(CommentImageCreateSerializer):
    """Сериализатор для получения фото комментариев."""

    class Meta(CommentImageCreateSerializer.Meta):
        """Настройки сериализатора."""

        fields = CommentImageCreateSerializer.Meta.fields + ("id",)  # type: ignore  # noqa: PGH003, RUF005


class CommentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания комментария."""

    images = CommentImageAddSerializer(many=True, required=False)

    class Meta:
        """Настройки сериализатора."""

        model = Comment
        fields = ("rating", "feedback", "images")

    def create(self, validated_data: dict) -> Comment:
        """Создать комментарий.

        Args:
            validated_data (dict): исходные данные

        Returns:
            Comment: созданный комментарий

        """
        if "images" not in validated_data:
            return Comment.objects.create(**validated_data)
        images = validated_data.pop("images")
        comment = Comment.objects.create(**validated_data)
        for image in images:
            img_serializer = CommentImageCreateSerializer(data=image)
            if img_serializer.is_valid(raise_exception=True):
                img_serializer.save(comment=comment)
        return comment

    def validate_images(self, data: list[str]) -> list[str]:
        """Валидровать изображения.

        Args:
            data (list[str]): изображения в формате base64

        Returns:
            list[str]: изображения в формате base64

        """
        validate_file_quantity(data)
        for img in data:
            validate_base64_field(img["image"])
            img_format, _ = img["image"].split(";base64,")
            ext = img_format.split("/")[-1]
            validate_extention(ext)
        return data


class CommentForModerationSerializer(CommentCreateSerializer):
    """Сериализатор для модерации комментариев."""

    images = CommentImageRetrieveSerializer(many=True, read_only=True)

    class Meta(CommentCreateSerializer.Meta):
        """Настройки сериализатора."""

        fields = CommentCreateSerializer.Meta.fields + ("id", "images")  # type: ignore  # noqa: PGH003, RUF005


class CommentReadSerializer(CommentForModerationSerializer):
    """Сериализатор для чтения комментария."""

    author = UserReadSerializer(read_only=True)
    obj_type = serializers.SerializerMethodField()
    title = serializers.CharField(source="subject.title")

    class Meta(CommentForModerationSerializer.Meta):
        """Настройки сериализатора."""

        fields = (
            CommentCreateSerializer.Meta.fields  # type: ignore  # noqa: PGH003, RUF005
            + (
                "author",
                "object_id",
                "title",
                "obj_type",
            )
        )

    def get_obj_type(self, obj: Comment) -> str:
        """Получить тип объекта, к которому комментарий относится.

        Args:
            obj (Comment): экземпляр комментария

        Returns:
            str(): тип объекта, к которому комментарий относится

        """
        return obj.subject.__class__.__name__.lower()
