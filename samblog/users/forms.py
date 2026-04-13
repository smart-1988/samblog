from datetime import datetime

from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.forms import TextInput, PasswordInput


class LoginUserForm(AuthenticationForm):
    """
    Форма для входа на сайт
    """

    username = forms.CharField(max_length=100, label='Логин', widget=TextInput(attrs={'style': 'form-input', "autofocus": True}))
    password = forms.CharField(max_length=100, label='Пароль', widget=PasswordInput(attrs={'style': 'form-input'}))
    captcha = CaptchaField(label='Капча')


class RegisterUserForm(UserCreationForm):
    """
    Форма для регистрации нового пользователя
    """

    username = forms.CharField(label='Логин', max_length=100, min_length=5)
    email = forms.CharField(label='Электронная почта', max_length=100, min_length=5, required=True)
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput)
    captcha = CaptchaField(label='Капча')

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }

    def clean_email(self):
        """
        Функуия проверки уникальности email
        """

        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError("Такой email уже зарегистрирован")
        return email


class ProfileUserForm(forms.ModelForm):
    """
    Форма для редактирования пользователя
    """

    this_year = datetime.today().year
    date_birth = forms.DateField(widget=forms.SelectDateWidget(years=tuple(range(this_year-100, this_year-5))), label='Дата рождения')
    username = forms.CharField(label='Логин', disabled=True)
    email = forms.CharField(label='Email', disabled=True, required=False)

    def clean_photo(self):
        if self.cleaned_data['photo']:
            filesize = self.cleaned_data['photo'].size
            if filesize > 10485760:  # 10 МБ в байтах
                raise ValidationError("Максимальный размер изображения 10 МБ")
        return self.cleaned_data['photo']

    class Meta:
        model = get_user_model()
        fields = ['photo', 'username', 'email', 'first_name', 'last_name', 'date_birth']


class UserPasswordChangeForm(PasswordChangeForm):
    pass

# class RegisterUserForm(forms.ModelForm):
#     """Форма для регистрации нового пользователя"""
#     username = forms.CharField(label='Логин', max_length=100, min_length=5)
#     password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
#     password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput)
#
#     class Meta:
#         model = get_user_model()
#         fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2']
#         labels = {
#             'email': 'Электронная почта',
#             'first_name': 'Имя',
#             'last_name': 'Фамилия',
#         }
#
#     def  clean_password2(self):
#         """Функция проверки правильности повтора пароля"""
#         cd = self.cleaned_data
#         if cd['password'] != cd['password2']:
#             raise ValidationError("Пароли не совпадают")
#         return cd['password']
#
#
#     def clean_email(self):
#         """Функуия проверки уникальности email"""
#         email = self.cleaned_data['email']
#         if get_user_model().objects.filter(email=email).exists():
#             raise ValidationError("Такой email уже зарегистрирован")
#         return email