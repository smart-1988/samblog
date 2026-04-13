from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, FormView, CreateView, UpdateView, DeleteView

from blog.forms import AddPostForm, FeedbackForm
from blog.models import Posts, Category, TagPost, UploadFiles, Feedback, SiteDescriptions, Certificates
from blog.utils import DataMixin, UserPermissionMixin, email
from django.core.cache import cache
from django.contrib.postgres.search import SearchVector


class BlogHome(DataMixin, ListView):
    """Домашняя страница"""

    title_page = 'Главная страница'
    cat_selected = 0
    context_object_name = 'posts'
    template_name = 'blog/index.html'

    def get_queryset(self):
        post_list = cache.get('blog_posts')     # Кеширование на уровне представления
        if not post_list:
            post_list = Posts.published.all().select_related('cat', 'author')
            cache.set('blog_posts', post_list, self.cache_time)
        return post_list


class SearchView(BlogHome):
    """Поиск по полям title и content"""

    cat_selected = None
    paginate_by = 0

    def get_queryset(self):
        if not self.request.GET:
            search_string = self.request.user.username
        else:
            search_string = self.request.GET['search_string']
        if search_string:
            self.extra_context = {'title': f'Результаты поиска "{search_string}":'}
        else:
            self.extra_context = {'title': 'Ничего не найдено'}
        post_list = cache.get('blog_posts')     # Кеширование на уровне представления
        if not post_list:
            post_list = Posts.objects.annotate(
                search=SearchVector("title", "content", "author__username", 'cat__name')
                ).filter(search=search_string).select_related('cat', 'author')

        return post_list


class AddPage(LoginRequiredMixin, DataMixin, CreateView):
    """Страница добавления нового поста"""

    template_name = "blog/add_content.html"
    form_class = AddPostForm
    # success_url = reverse_lazy('home')
    title_page = 'Добавить пост'
    # permission_required = 'blog.add_posts'  # разрешение на добавление нового поста


    def form_valid(self, form):
        w = form.save(commit=False)
        w.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, cat_selected=None)


class EditPage(UserPermissionMixin, DataMixin, UpdateView):
    """Страница редактирования поста"""

    model = Posts
    form_class = AddPostForm
    template_name = 'blog/add_content.html'
    slug_url_kwarg = 'post_slug'
    # fields = ['title', 'content', 'photo', 'content', 'cat', 'stuff', 'tags'] # При подключении формы поля не указываются
    title_page = 'Редактировать пост'
    permission_required = 'blog.change_posts'   # разрешение на изменение поста

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, cat_selected=None, slug=context['object'].slug)


class DeletePost(UserPermissionMixin, DataMixin, DeleteView):
    """Страница удаления поста"""

    model = Posts
    template_name = 'blog/delete_post.html'
    success_url = reverse_lazy("home")
    context_object_name = 'post'
    title_page = 'Удалить пост'
    permission_required = 'blog.delete_posts'   # разрешение на удаление поста

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, cat_selected=None)


class ShowCategory(DataMixin, ListView):
    """Страница просмотра постов в зависимости от выбранной категории"""

    template_name = 'blog/index.html'
    context_object_name = 'posts'
    allow_empty = False


    def get_queryset(self):
        cat = Category.objects.get(slug=self.kwargs['cat_slug'])
        post_list = Posts.published.filter(cat=cat).select_related('cat', 'author')
        self.extra_context = {'title': 'Категория: ' + cat.name,
                                      'cat_selected': cat.pk}
        return post_list

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     cat = context['posts'][0].cat
    #     return self.get_mixin_context(context,
    #                                   title='Категория: ' + cat.name,
    #                                   cat_selected = cat.pk)


class ShowPost(DataMixin, DetailView):
    """Страница просмотра поста"""

    # model = Posts     # Определил функцию get_object для отображения только опубликованных постов
    template_name = 'blog/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=context['post'].title)

    def get_object(self, queryset=None):
        return get_object_or_404(Posts.published, slug=self.kwargs[self.slug_url_kwarg])


class TagPostList(DataMixin, ListView):
    """Страница просмотра постов в зависимости от выбранного тега"""

    template_name = 'blog/index.html'
    context_object_name = 'posts'
    title_page = 'Тег : '

    def get_queryset(self):
        tag = TagPost.objects.get(slug=self.kwargs['tag_slug'])
        return tag.tags.filter(is_published=Posts.Status.PUBLISHED).select_related('cat')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = TagPost.objects.get(slug=self.kwargs['tag_slug'])
        return self.get_mixin_context(context, title=self.title_page + tag.title,)


class FeedbackView(DataMixin, CreateView):
    """Страница обратной связи"""

    model = Feedback
    success_url = reverse_lazy('success_feedback')
    form_class = FeedbackForm
    template_name = 'blog/feedback.html'
    title_page = 'Обратная связь'

    def form_valid(self, form):
        data = form.data
        subject = f'Сообщение с формы обратной связи на сайте samblog.ru. Отправитель {data["last_name"]} {data["first_name"]}, {data["email"]}.'
        email(subject, data['message'])
        return super().form_valid(form)


def success_feedback(request):
    """Страница успешной отправки формы обратной связи"""

    return render(request, 'blog/success_feedback.html', {'title': 'Сообщение отправлено!'})


class AboutSiteView(DataMixin, DetailView):
    """Страница о сайте"""

    pk = 1
    template_name = 'blog/about_site.html'
    title_page = 'О сайте'
    context_object_name = 'content' # Замена стандартного имени переменной "object" в шаблоне

    def get_object(self, queryset=None):
        return get_object_or_404(SiteDescriptions.objects, pk=self.pk)


class AboutAuthorView(AboutSiteView):
    """Страница об авторе"""

    pk = 2
    template_name = 'blog/about.html'
    title_page = 'Об авторе'

    def get_context_data(self, **kwargs):
        """Добавление второй модели с сертификатами в контекст"""
        context = super(AboutAuthorView, self).get_context_data(**kwargs)
        context['certs'] = Certificates.objects.all()
        return context


def page_not_found(request, exception):
    """Отбивка 404"""

    return render(request, 'blog/index.html', context={'title': "Страница не найдена"})