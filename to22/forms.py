from django import forms
from . import models
from .models import Division, Postdata, Good, Item, User
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm, PasswordChangeForm,
    PasswordResetForm, SetPasswordForm
)
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginForm(AuthenticationForm):
    """ログインフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる


class UserCreateForm(UserCreationForm):
    """ユーザー登録用フォーム"""

    class Meta:
        model = User
        if User.USERNAME_FIELD == 'email':
            fields = ('email',)
        else:
            fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UserUpdateForm(forms.ModelForm):
    """ユーザー情報更新フォーム"""

    class Meta:
        model = User
        if User.USERNAME_FIELD == 'email':
            fields = ('icon', 'email', 'first_name', 'last_name')
        else:
            fields = ('icon', 'username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MyPasswordChangeForm(PasswordChangeForm):
    """パスワード変更フォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MyPasswordResetForm(PasswordResetForm):
    """パスワード忘れたときのフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MySetPasswordForm(SetPasswordForm):
    """パスワード再設定用フォーム(パスワード忘れて再設定)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class PostForm(forms.Form):
    division_id = forms.ModelChoiceField(models.Division.objects, label='言語', to_field_name='id')
    item_id = forms.ModelChoiceField(models.Item.objects, label='教材', to_field_name='id')
    time =  forms.IntegerField(min_value=1, max_value=1440, label='学習時間(分)')
    memo = forms.CharField(max_length=100, help_text='感想を100文字以内でどうぞ')
        
class DivisionForm(forms.Form):
    division_id = forms.ModelChoiceField(models.Division.objects, label='言語', to_field_name='id')

class ItemForm(forms.Form):
    name = forms.CharField(max_length=100)
    URL = forms.URLField(required=False)
    division_id = forms.ModelChoiceField(models.Division.objects, label='言語', to_field_name='id')
    
    def __str__(self):
        return self.name

class FindForm(forms.Form):
    find = forms.CharField(label='Find', required=False)
