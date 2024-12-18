from django.contrib.auth.base_user import BaseUserManager

from core.choices import Role


class UserManager(BaseUserManager):
    """Кастомный менеджер для модели пользователя."""

    def create_user(self, email, password, **kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.is_active = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        username = input("Введите имя пользователя: ")
        extra_fields.setdefault("username", username)
        user = self.create_user(email=email, password=password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.role = Role.ADMIN
        user.save(using=self._db)
        return user
