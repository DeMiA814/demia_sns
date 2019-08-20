from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin, AbstractUser, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

# カスタムユーザー
class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.
    Username and password are required. Other fields are optional.
    """
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=100, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    icon = models.ImageField(_('icon'),
        upload_to='img/',
        blank=True,
        null=True,
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        #abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def get_icon(self):
        return self.icon

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

class Division(models.Model):
    name = models.CharField(max_length=55)
    user_id = models.ManyToManyField(User, related_name='user_id_division')
        
    def __str__(self):
        return self.name

# 教材
class Item(models.Model):
    name = models.CharField(max_length=100)
    URL = models.URLField(blank=True, null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_id_item', default='')
    division_id = models.ForeignKey(Division, on_delete=models.CASCADE, null=True, related_name='division_id_item')
    is_active = models.BooleanField(default=True,)
    
    def __str__(self):
        return self.name

# 投稿
class Postdata(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.SET_NULL, related_name='user_id_postdata', null=True)
    time = models.IntegerField(blank=True)
    good_count = models.IntegerField(default=0)
    date = models.DateField(default=timezone.now)
    division_id = models.ForeignKey(Division, on_delete=models.CASCADE, blank=True, null=True, related_name='dvision_id_postdata')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='user_id_postdata')
    memo = models.TextField(blank=True, null=True)
    
# いいね（未実装）
class Good(models.Model):
    postdata_id = models.ForeignKey(Postdata, on_delete=models.CASCADE, related_name='postdata_id_good')
    user_id = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='user_id_good', null=True)

