from django.contrib.auth.base_user import BaseUserManager

from core.choices import Role


class UserManager(BaseUserManager):
    """Кастомный менеджер для модели пользователя."""

    def create_user(self, email, password):
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        print(user)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=email,
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.role = Role.ADMIN
        user.save(using=self._db)
        return user
