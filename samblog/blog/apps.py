from django.apps import AppConfig


class BlogConfig(AppConfig):
    verbose_name = 'Блог'       # Отображение имени модели в админке
    name = 'blog'
