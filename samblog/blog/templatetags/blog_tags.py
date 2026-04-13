from django import template
from django.db.models import Count

import blog.views as views
from blog.models import Category, TagPost

register = template.Library()


@register.simple_tag()
def get_categories():
    return views.cats_db


@register.inclusion_tag('blog/list_categories.html')
def show_categories(cat_selected=None):
    cats = Category.objects.annotate(cnt=Count('posts')).filter(cnt__gt=0).order_by('name')
    return {'categories': cats, 'cat_selected': cat_selected}


@register.inclusion_tag('blog/list_tags.html')
def show_tags():
    return {'tags': TagPost.objects.annotate(cnt=Count('tags')).filter(cnt__gt=0)}
