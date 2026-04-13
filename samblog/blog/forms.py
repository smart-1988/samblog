from captcha.fields import CaptchaField
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from blog.models import Category, Stuff, Posts, TagPost, Feedback


class AddPostForm(forms.ModelForm):
    cat = forms.ModelChoiceField(Category.objects.all(), empty_label='Выбери категорию', label='Категория')
    stuff = forms.ModelChoiceField(Stuff.objects.all(), required=False, empty_label='Не выбрано', label='Материалы')
    tags = forms.ModelMultipleChoiceField(TagPost.objects.all(), required=False, label='Теги')
    captcha = CaptchaField(label='Капча')

    class Meta:
        model = Posts
        fields = ['title', 'content', 'photo', 'is_published', 'cat', 'stuff', 'tags']
        widget = {
            'title': forms.TextInput(attrs={'style': 'form-input'}),
            'content': forms.Textarea(attrs={'cols': 73, 'rows': 6})
        }
        # labels = {'slug': 'URL'}

    def clean_title(self):  # Пользовательский валидатор. Проверяет длину заголовка
        title = self.cleaned_data['title']
        if 5 <=len(title) <= 50:
            return title
        raise ValidationError('Заголовок должен быть от 5 до 50 символов')

    def clean_photo(self):  # Пользовательский валидатор. Проверяет размер изображения
        if self.cleaned_data['photo']:
            filesize = self.cleaned_data['photo'].size
            if filesize > 10485760:  # 10 МБ в байтах
                raise ValidationError("Максимальный размер изображения 10 МБ")
        return self.cleaned_data['photo']


# class UploadFileForm(forms.Form):
#     file = forms.ImageField(label='Файл')


class FeedbackForm(forms.ModelForm):
    captcha = CaptchaField(label='Капча')

    class Meta:
        model = Feedback
        fields = ['first_name', 'last_name', 'email', 'message']
        widgets = {
            'message': forms.Textarea(
                attrs={
                    'placeholder': 'Напишите тут ваше сообщение',
                    'id': 'id_content',
                }
            )
        }