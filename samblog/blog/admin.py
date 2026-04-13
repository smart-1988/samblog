from django.contrib import admin, messages
from django.db.models.functions import Length
from django.utils.safestring import mark_safe

from .models import Posts, Category, TagPost, Feedback, SiteDescriptions, Certificates


# Register your models here.
class StuffFilter(admin.SimpleListFilter):
    title = 'Наличие дополнительных материалов'
    parameter_name = 'stuff'

    def lookups(self, request, model_admin):
        return[
            ('exist', 'Есть дополнительные материалы'),
            ('does not exist', 'Нет дополнительных материалов')
        ]
    def queryset(self, request, queryset):
        if self.value() == 'exist':
            return queryset.filter(stuff__isnull=False)

        if self.value() == 'does not exist':
            return queryset.filter(stuff__isnull=True)


@admin.register(Posts)
class PostsAdmin(admin.ModelAdmin):
    list_display = ('title', 'time_create', 'time_update', 'is_published', 'cat', 'post_photo', 'author__username')
    list_display_links = ('title',)
    fields = ('title', 'author', 'content', 'slug', 'post_photo', 'is_published', 'cat', 'stuff', 'tags')
    readonly_fields = ('slug', 'post_photo', 'author')
    filter_horizontal = ('tags',)
    ordering = ('time_create', 'is_published')
    list_editable = ('is_published',)
    list_per_page = 10      # Пагинация
    actions = ('set_published', 'set_draft')
    search_fields = ('title', 'cat__name')
    list_filter = ('cat__name', 'is_published', StuffFilter)
    save_on_top = True

    @admin.display(description='Фото', ordering='id')
    def post_photo(self, post: Posts):
        if post.photo:
            return mark_safe(f"<img src='{post.photo.url}' width=100>")
        return 'Без фото'

    @admin.action(description='Опубликовать')
    def set_published(self, request, queryset):
        count = queryset.update(is_published=Posts.Status.PUBLISHED)
        self.message_user(request, f'Опубликовано {count} записей')

    @admin.action(description='Снять с публикации')
    def set_draft(self, request, queryset):
        count = queryset.update(is_published=Posts.Status.DRAFT)
        self.message_user(request, f'Снято с публикации {count} записей', messages.WARNING)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(TagPost)
class TagPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Feedback)
class TagPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'complete')
    list_display_links = ('id', 'email')


@admin.register(SiteDescriptions)
class SiteDescriptionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')


@admin.register(Certificates)
class CertificatesAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'year', 'url', 'cert_image')
    list_display_links = ('id', 'title', 'year', 'url')

    @admin.display(description='Изображение', ordering='id')
    def cert_image(self, certs: Certificates):
        if certs.image:
            return mark_safe(f"<img src='{certs.image.url}' width=100>")
        return 'Нет изображения'