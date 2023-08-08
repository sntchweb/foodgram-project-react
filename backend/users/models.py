from django.contrib.auth.models import AbstractUser

from django.db.models import (CASCADE, CharField, EmailField, ForeignKey,
                              Model, UniqueConstraint)


class User(AbstractUser):
    email = EmailField(
        verbose_name='Электронная почта',
        max_length=254,
        unique=True
    )
    username = CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True
    )
    first_name = CharField(
        verbose_name='Имя',
        max_length=150
    )
    last_name = CharField(
        verbose_name='Фамилия',
        max_length=150
    )
    password = CharField(
        verbose_name='Пароль',
        max_length=150
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'password', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscription(Model):
    """Модель для подписки."""

    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
