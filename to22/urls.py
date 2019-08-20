from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('post', views.post, name="post"),
    path('report', views.report, name="report"),
    path('submit', views.submit, name="submit"),
    path('user',views.user, name="user"),   
    path('register/login/', views.Login.as_view(), name='login'),
    path('register/logout/', views.Logout.as_view(), name='logout'),
    path('register/user_create/', views.UserCreate.as_view(), name='user_create'),
    path('register/user_create/done/', views.UserCreateDone.as_view(), name='user_create_done'),
    path('register/user_create/complete/<token>/', views.UserCreateComplete.as_view(), name='user_create_complete'),
    path('register/user_detail/<int:pk>/', views.UserDetail.as_view(), name='user_detail'),
    path('register/user_update/<int:pk>/', views.UserUpdate.as_view(), name='user_update'),
    path('register/password_change/', views.PasswordChange.as_view(), name='password_change'),
    path('register/password_change/done/', views.PasswordChangeDone.as_view(), name='password_change_done'),
    path('register/password_reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('register/password_reset/done/', views.PasswordResetDone.as_view(), name='password_reset_done'),
    path('register/password_reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('register/password_reset/complete/', views.PasswordResetComplete.as_view(), name='password_reset_complete'),
    path('edit/<int:num>',views.edit,name='edit'),
    path('delete/<int:num>',views.delete,name='delete'),
]
