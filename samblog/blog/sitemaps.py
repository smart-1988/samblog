from django.contrib.sitemaps import Sitemap
from blog.models import Posts, Category, TagPost


class BlogSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.9

    def items(self):
        return Posts.published.all()

    def lastmod(self, obj):
        return obj.time_update

class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Category.objects.all()

class TagsSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return TagPost.objects.all()