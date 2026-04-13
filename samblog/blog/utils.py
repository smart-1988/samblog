from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.mail import send_mail
from django.http import Http404


menu = [
    {'title': 'samblog.ru', 'url_name': 'home'},
    {'title': 'Добавить статью', 'url_name': 'add_content'},
    {'title': 'Об авторе', 'url_name': 'about'},
    {'title': 'О сайте', 'url_name': 'about_site'},
]


class DataMixin:
    """Миксин, определяющий общие параметры для представлений"""

    paginate_by = 3
    title_page = None
    cat_selected = None
    extra_context = {}
    cache_time = 10

    def __init__(self):
        if self.title_page:
            self.extra_context['title'] = self.title_page

        if self.cat_selected is not None:
            self.extra_context['cat_selected'] = self.cat_selected

        if 'menu' not in self.extra_context:
            self.extra_context['menu'] = menu

    def get_mixin_context(self, context, **kwargs):
        context['menu'] = menu
        context['cat_selected'] = None
        context.update(kwargs)
        return context


class UserPermissionMixin(UserPassesTestMixin):
    """Миксин, проверяющий, есть ли у пользователя права на изменение, удаление постов"""

    permission_required = None

    def test_func(self):
        """
        Проверяет условие, при которой тест будет пройден, и вернёт True.
        В данном случае, если пользователь является автором статьи, или у пользователя есть нужные разрешения, вернётся True
        """
        post = self.get_object()
        return (
                self.request.user == post.author or
                self.request.user.has_perm(self.permission_required)
        )

    def handle_no_permission(self):
        """Генерируем ошибку 404, если тест не будет пройден"""
        raise Http404



def email(subject, content):            # Функция отправки письма с содержимым формы обратной связи
   send_mail(subject,
      content,
      'yndx-sm-art@yandex.ru',
      ['almostem@mail.ru']
   )
