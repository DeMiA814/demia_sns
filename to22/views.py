from django.shortcuts import render
from .models import Division, Postdata, Good, Item, User
from .forms import PostForm,DivisionForm,ItemForm,FindForm
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.db.models import Q
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect, resolve_url
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views import generic
from .forms import (
    LoginForm, UserCreateForm, UserUpdateForm, MyPasswordChangeForm,
    MyPasswordResetForm, MySetPasswordForm
)
from django.contrib.auth.decorators import login_required
import json
import csv

# Create your views here.

User = get_user_model()

# /register下
class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'register/login.html'


class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    template_name = 'to22/index.html'


class UserCreate(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'register/user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject_template = get_template('register/mail_template/create/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template('register/mail_template/create/message.txt')
        message = message_template.render(context)
        
        from_email = settings.EMAIL_HOST_USER

        user.email_user(subject, message, from_email)
        return redirect('user_create_done')


class UserCreateDone(generic.TemplateView):
    """ユーザー仮登録したよ"""
    template_name = 'register/user_create_done.html'


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'register/user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoenNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # まだ仮登録で、他に問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()


class OnlyYouMixin(UserPassesTestMixin):
    """本人か、スーパーユーザーだけユーザーページアクセスを許可する"""
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser


class UserDetail(OnlyYouMixin, generic.DetailView):
    """ユーザーの詳細ページ"""
    model = User
    template_name = 'register/user_detail.html'  # デフォルトユーザーを使う場合に備え、きちんとtemplate名を書く


class UserUpdate(OnlyYouMixin, generic.UpdateView):
    """ユーザー情報更新ページ"""
    model = User
    form_class = UserUpdateForm
    template_name = 'register/user_form.html'  # デフォルトユーザーを使う場合に備え、きちんとtemplate名を書く

    def get_success_url(self):
        return resolve_url('user_detail', pk=self.kwargs['pk'])


class PasswordChange(PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('password_change_done')
    template_name = 'register/password_change.html'


class PasswordChangeDone(PasswordChangeDoneView):
    """パスワード変更しました"""
    template_name = 'register/password_change_done.html'


class PasswordReset(PasswordResetView):
    """パスワード変更用URLの送付ページ"""
    subject_template_name = 'register/mail_template/password_reset/subject.txt'
    email_template_name = 'register/mail_template/password_reset/message.txt'
    template_name = 'register/password_reset_form.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('password_reset_done')


class PasswordResetDone(PasswordResetDoneView):
    """パスワード変更用URLを送りましたページ"""
    template_name = 'register/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    """新パスワード入力ページ"""
    form_class = MySetPasswordForm
    success_url = reverse_lazy('password_reset_complete')
    template_name = 'register/password_reset_confirm.html'


class PasswordResetComplete(PasswordResetCompleteView):
    """新パスワード設定しましたページ"""
    template_name = 'register/password_reset_complete.html'

""""""



# /to22下

# トップページ
def index(request):
    division_flag = True
    if not request.user.is_authenticated: # ログインしていないユーザー
        post_info = Postdata.objects.all().order_by('-id')
        msg = ''
        form = FindForm()
    else: # ログイン済みのユーザー
        user_group = Division.objects.filter(user_id=request.user) # ユーザーが登録している言語
        count = list(user_group) # ユーザーが登録している言語の数 → 0ならメッセージ表示
        post_info = Postdata.objects.filter(division_id__in=user_group).order_by('-id')
        if len(count) == 0:
            division_flag = False

        # 検索
        if (request.method == 'POST'):
            msg = '検索結果:'
            form = FindForm(request.POST)
            str = request.POST['find']
            item_group = Item.objects.filter(name__contains=str)
            post_info = Postdata.objects.filter(item_id__in=item_group,division_id__in=user_group).order_by('-id')
        else:
            msg = '検索してください'
            form = FindForm()
            post_info = Postdata.objects.filter(division_id__in=user_group).order_by('-id')
            
    params = {
        'division_flag':division_flag,
        'post_info':post_info,
        'message':msg,
        'form':form,
        
    }
    return render(request, 'to22/index.html', params)

# 投稿ページ
@login_required(login_url='/to22/register/login')
def post(request):
    form = PostForm()
    form.fields['item_id'].queryset = Item.objects.filter(user_id=request.user)
    
    # 投稿ボタンが押された時
    if request.method == 'POST':
        sel_item = request.POST['item_id']
        sel_division = Division.objects.get(division_id_item=sel_item)
        post_memo = request.POST['memo']
        post_time = request.POST['time']
        postdata = Postdata()
        postdata.item_id = Item.objects.get(id=sel_item)
        postdata.division_id = sel_division
        postdata.memo = post_memo
        postdata.time = post_time
        postdata.user_id = request.user
        postdata.save()
        form = PostForm()

    params = {
        'form':form,
    }
    return render(request, 'to22/post.html', params)

# 学習の記録ページ
@login_required(login_url='/to22/register/login')
def report(request):
    report_post = Postdata.objects.filter(user_id=request.user) # ユーザーの投稿を取ってくる
    division_time = {}
    for post in report_post:
        if post.division_id in division_time.keys():
            division_time[post.division_id] += post.time
        else:
            division_time[post.division_id] = post.time

    division_list_pre = list(division_time.keys())
    division_only =[]
    for division in division_list_pre:
        division_only.append(division.name)

    time_sum = 0
    for time in list(division_time.values()):
        time_sum += time

    time_hour = 0
    time_hour_list =[]
    for minute in list(division_time.values()):
        hour = minute // 60
        time_hour_list.append(hour)

    params = {
        'report_post':report_post,
        'division_time':division_time,
        'time_sum':time_sum,
        'division_list':json.dumps(division_only),
        'time_list':list(division_time.values()),
        'time_hour_list':time_hour_list,
    }
    return render(request, 'to22/report.html', params)

# 教材登録ページ
@login_required(login_url='/to22/register/login')
def submit(request):
    form = ItemForm()
    form.fields['division_id'].queryset = Division.objects.filter(user_id=request.user)
    
    # ボタンが押された時
    if request.method == 'POST':
        if 'add_btn' in request.POST: # 教材を追加
            item_name = request.POST['name']
            picture_url = request.POST['URL']
            division_name = request.POST['division_id']
            
            itemdata = Item()
            itemdata.name = item_name
            itemdata.URL = picture_url
            itemdata.division_id = Division.objects.get(id=division_name)
            itemdata.user_id = request.user
            itemdata.is_active = True
            itemdata.save()

        elif 'delete_btn' in request.POST: # 教材を削除
            item_delete = request.POST['item']
            itemdata = Item.objects.get(id=item_delete)
            itemdata.delete()
        
        elif 'change_state_btn' in request.POST: # 使用中の教材 ↔ 終わった教材
            item_changeing_state = request.POST['item']
            itemdata = Item.objects.get(id=item_changeing_state)
            itemdata.is_active = not itemdata.is_active
            itemdata.save()

    active_items = Item.objects.filter(is_active=True, user_id=request.user).order_by('-id')
    not_active_items = Item.objects.filter(is_active=False, user_id=request.user).order_by('-id')
    
    params = {
        'form':form,
        'data':[],
        'active_items':active_items,
        'not_active_items':not_active_items,
    }
    return render(request, 'to22/submit.html',params)


# ユーザーページ
@login_required(login_url='/to22/register/login')
def user(request):
    user_post_info = Postdata.objects.filter(user_id=request.user).order_by('-id')
    data = Division.objects.all()
    skill = Division.objects.filter(user_id=request.user)
    delete_menu = DivisionForm()
    delete_menu.fields['division_id'].queryset = Division.objects.filter(user_id=request.user)
    form = DivisionForm()
    
    if request.method == 'POST':
        if request.POST['mode'] == '検索': # 言語検索ボタン
            word = request.POST.get('word')
            form.fields['division_id'].queryset = Division.objects.filter(name__contains=word)

        elif request.POST['mode'] == 'add': # 言語追加ボタン
            division_name = request.POST['division_id']
            divisiondata = Division.objects.get(id=division_name)
            divisiondata.save()
            divisiondata.user_id.add(request.user)
            data = Division.objects.all()
            form = DivisionForm(request.POST)
            
        elif request.POST['mode'] == 'delete': # 言語削除ボタン
            division_name = request.POST['division_id']
            divisiondata = Division.objects.get(id=division_name)
            divisiondata.save()
            divisiondata.user_id.remove(request.user)
            data = Division.objects.all()
            form = DivisionForm(request.POST)
    
    params = {
        'delete_menu':delete_menu,
        'skill':skill,
        'form':form,
        'data':data,
        'user_post_info':user_post_info,
    }
    
    return render(request, 'to22/user.html', params)

# 投稿編集ページ（ユーザーページからのリンク）
@login_required(login_url='/to22/register/login')
def edit(request,num):
    postdata = Postdata.objects.get(id=num)
    if request.method == 'POST':
        sel_item = request.POST['item_id']
        sel_division = Division.objects.get(division_id_item=sel_item)
        post_memo = request.POST['memo']
        post_time = request.POST['time']
        postdata.item_id = Item.objects.get(id=sel_item)
        postdata.division_id = sel_division
        postdata.memo = post_memo
        postdata.time = post_time
        postdata.user_id = request.user
        postdata.save()
        return redirect(to='/to22/user')
    
    else:
        form = PostForm(
            initial = {
                'item_id': postdata.item_id,
                'memo':postdata.memo,
                'time':postdata.time,
            })
        
    
    params = {
        'id':num,
        'form':form,
        
    }
    return render(request, 'to22/edit.html', params)

# 投稿削除ページ（ユーザーページからのリンク）
@login_required(login_url='/to22/register/login')
def delete(request,num):
    obj = Postdata.objects.get(id=num)
    if (request.method == 'POST'):
        obj.delete()
        return redirect(to='/to22/user')
    
    params = {
        'id':num,
    }
    return render(request, 'to22/delete.html', params)

def check_pwa(request):
    return render(request, 'to22/assetlinks.json', {})
