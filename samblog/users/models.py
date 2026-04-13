from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    """Расширяем стандартную модель User"""

    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    photo = models.ImageField(blank=True, null=True, upload_to='users/%Y/%m/%d/', verbose_name='Фото')
    date_birth = models.DateTimeField(blank=True, null=True, verbose_name='Дата рождения')