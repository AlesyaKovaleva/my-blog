from django import forms
from .models import Post, Comment, Author
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text', 'image',)


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class AuthorForm(forms.ModelForm):

    class Meta:
        model = Author
        fields = ('nickname', 'first_name', 'last_name', 'birth_date',
                  'country', 'gender', 'author_info', 'avatar',)

        widgets = {
            'birth_date': forms.TextInput(attrs={'type': 'date'})
        }


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, label='Имя', help_text='Введите своё имя')
    last_name = forms.CharField(max_length=30, required=False, label='Фамилия', help_text='Введите свою фамилию')
    email = forms.EmailField(max_length=254, help_text='Введите действительный адрес электронной почты')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
