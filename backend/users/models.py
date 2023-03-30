from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Класс пользователей."""

    email = models.EmailField(
        'email address',
        max_length=254,
        unique=True,
        blank=False,
        error_messages={
            'unique': _('Пользователь с таким email уже существует!'),
        },
        help_text=_('Укажите свой email'),
    )
    username = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True,
        db_index=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Пользователь с таким никнеймом уже существует!'
        )]
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        blank=True,
        help_text=_('Укажите свою имя'),
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        blank=True,
        help_text=_('Укажите свою фамилию'),
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Класс подписчиков и автора."""

    user = models.ForeignKey(
        User,
        related_name='subscriber',
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='subscribing',
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'Автор: {self.author}, подписчик: {self.user}'

    def save(self, **kwargs):
        if self.user == self.author:
            raise ValidationError("Невозможно подписаться на себя")
        super().save()

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_subscriber')
        ]
