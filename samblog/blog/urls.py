from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.urls import path, register_converter, include

from blog.views import BlogHome, ShowCategory, TagPostList, ShowPost, AddPage, EditPage, DeletePost, SearchView, \
    FeedbackView, success_feedback, AboutAuthorView, AboutSiteView
from . import converters
from .sitemaps import BlogSitemap, CategorySitemap, TagsSitemap

register_converter(converters.FourDigitsYearConverter, 'year4')

urlpatterns = [
    path('', BlogHome.as_view(), name='home'),
    path('search/', SearchView.as_view(), name='search'),
    path('add-content/', AddPage.as_view(), name='add_content'),
    path('edit/<slug:post_slug>', EditPage.as_view(), name='edit_content'),
    path('delete/<slug:slug>', DeletePost.as_view(), name='delete_content'),
    path('about/', AboutAuthorView.as_view(), name='about'),
    path('about_site/', AboutSiteView.as_view(), name='about_site'),
    path('post/<slug:post_slug>', ShowPost.as_view(), name='post'),
    path('category/<slug:cat_slug>', ShowCategory.as_view(), name='get_category'),
    path('tag/<slug:tag_slug>', TagPostList.as_view(), name='show_tag'),
    path('feedback/', FeedbackView.as_view(), name='feedback'),
    path('feedback/success', success_feedback, name='success_feedback'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('captcha/', include('captcha.urls')),

    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": {
            'posts': BlogSitemap,
            'cats': CategorySitemap,
            'tags': TagsSitemap,
            }
        },
        name="django.contrib.sitemaps.views.sitemap",
    )
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

