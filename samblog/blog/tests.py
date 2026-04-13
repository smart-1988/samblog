from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from blog.models import Posts


# Create your tests here.
class GetPagesTestCase(TestCase):
    fixtures = ('blog_posts.json', 'blog_category.json', 'blog_tagpost.json', 'blog_stuff.json')
    def detUp(self):
        pass

    def test_mainpage(self):
        path = reverse('home')
        response = self.client.get(path)    # имитация запроса браузера
        self.assertTemplateUsed(response, 'blog/index.html')
        self.assertEqual('Главная страница', response.context_data['title'])
        self.assertEqual(response.status_code, 200)

    def test_redirect_addpage(self):
        path = reverse('add_content')
        redirect_uri = reverse('users:login') + '?next=' + path
        response = self.client.get(path)
        self.assertRedirects(response, redirect_uri)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_data_mainpage(self):
        path = reverse('home')
        posts = Posts.published.all().select_related('cat')
        response = self.client.get(path)
        self.assertQuerySetEqual(response.context_data['posts'], posts[:2])

    def test_paginate_mainpage(self):
        path = reverse('home')
        page = 2    # текущая страница
        paginate_by = 2
        posts = Posts.published.all().select_related('cat')
        response = self.client.get(path + f'?page={page}')
        self.assertQuerySetEqual(response.context_data['posts'], posts[(page-1)*paginate_by:page*paginate_by])

    def test_content_post(self):
        post = Posts.published.get(pk=1)
        path = reverse('post', args=[post.slug])
        response = self.client.get(path)
        self.assertEqual(response.context_data['post'].content, post.content)

    def tearDown(self):
        pass


