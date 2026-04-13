from django.contrib.auth import get_user_model
from django.db.models import PROTECT
from django.urls import reverse
from unidecode import unidecode
from django.db import models
from django.utils.text import slugify


class PublishedManager(models.Manager):
    """Пользовательский менеджер контекста. Фильтрует опубликованные записи."""

    def get_queryset(self):
        return super().get_queryset().filter(is_published=1)


class Posts(models.Model):
    """Основная модель. Посты"""

    class Status(models.IntegerChoices):
        """Возможность указывать параметр 'is_published' через 'Posts.Status.PUBLISHED'"""
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    title = models.CharField(max_length=100, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    content = models.TextField(blank=True, verbose_name='Содержание')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Время обновления')
    is_published = models.IntegerField(choices=Status.choices, default=Status.DRAFT, verbose_name='Статус')
    photo = models.ImageField(blank=True, default=None, upload_to='photos/%Y/%m/%d/', null=True, verbose_name='Фото')
    cat = models.ForeignKey('Category', on_delete=PROTECT, related_name='posts', verbose_name='Категория')
    tags = models.ManyToManyField('TagPost', blank=True, related_name='tags', verbose_name='Теги')
    stuff = models.OneToOneField('Stuff', null=True, blank=True, on_delete=models.SET_NULL, related_name='stuff',
                                 verbose_name='Дополнительные материалы')
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='posts', null=True,
                               default=None, verbose_name='Автор')

    objects = models.Manager()
    published = PublishedManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})


    def save(self, *args, **kwargs):
        # if not self.id:
        self.slug = slugify(unidecode(self.title))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Пост'            # Отображение имени записей модели в админке, единственное число
        verbose_name_plural = 'Посты'    # Отображение имени записей модели в админке, множественное число
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Имя категории')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='Слаг')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('get_category', kwargs={'cat_slug': self.slug})

    class Meta:
        verbose_name = 'Категория'              # Отображение имени записей модели в админке, единственное число
        verbose_name_plural = 'Категории'       # Отображение имени записей модели в админке, множественное число


class TagPost(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('show_tag', kwargs={'tag_slug': self.slug})

    class Meta:
        verbose_name = 'Тег'                  # Отображение имени записей модели в админке, единственное число
        verbose_name_plural = 'Теги'          # Отображение имени записей модели в админке, множественное число


class Stuff(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField(unique=True)

    def __str__(self):
        return self.title


class UploadFiles(models.Model):
    file = models.FileField(upload_to='upload_cover')


class Feedback(models.Model):
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    email = models.EmailField(max_length=50, verbose_name='Электронная почта')
    message = models.CharField(max_length=255, verbose_name='Сообщение')
    complete = models.BooleanField(default=False, verbose_name='Завершён')

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Фидбэк'            # Отображение имени записей модели в админке, единственное число
        verbose_name_plural = 'Фидбэки'    # Отображение имени записей модели в админке, множественное число


class SiteDescriptions(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название')
    content = models.TextField(verbose_name='Текст', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Описание'           # Отображение имени записей модели в админке, единственное число
        verbose_name_plural = 'Описания'    # Отображение имени записей модели в админке, множественное число


class Certificates(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название')
    year = models.DateField(verbose_name='Год получения')
    url = models.URLField(null=True, default=None, verbose_name='Ссылка')
    image = models.ImageField(blank=True, default=None, upload_to='certificates/', null=True, verbose_name='Изображение')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Сертификат'            # Отображение имени записей модели в админке, единственное число
        verbose_name_plural = 'Сертификаты'    # Отображение имени записей модели в админке, множественное число