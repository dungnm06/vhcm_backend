from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import datetime
from vhcm.biz.validation.string import only_digit


# Fields
ID = 'user_id'
USERNAME = 'username'
PASSWORD = 'password'
FULLNAME = 'fullname'
NATIONALITY = 'nationality'
PLACE_OF_BIRTH = 'place_of_birth'
DATE_OF_BIRTH = 'date_of_birth'
ADDRESS = 'address'
PHONE_NUMBER = 'phone_number'
EMAIL = 'email'
ID_NUMBER = 'id_number'
ADMIN = 'admin'
AVATAR = 'avatar'
ACTIVE = 'active'
FIRST_LOGIN = 'first_login'
CDATE = 'cdate'
MDATE = 'mdate'


class UserManager(BaseUserManager):
    def create_user(self, username, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not username:
            raise ValueError('Users must have an username')

        user = self.model(
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            username,
            password=password,
        )
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    user_id = models.AutoField(
        primary_key=True, verbose_name='user id', db_index=True
    )
    username = models.CharField(
        verbose_name='username', unique=True,
        max_length=20, db_index=True
    )
    fullname = models.CharField(
        verbose_name='fullname', max_length=60,
        db_index=True, default=''
    )
    nationality = models.CharField(
        verbose_name='nationality',
        max_length=60, blank=False,
        default='Vietnam'
    )
    place_of_birth = models.CharField(
        verbose_name='place of birth',
        max_length=255, blank=False,
        default=''
    )
    date_of_birth = models.DateField(
        verbose_name='date of birth',
        default=datetime.date.today
    )
    address = models.TextField(
        verbose_name='address', default=''
    )
    id_number = models.CharField(
        verbose_name='id_number',
        default='', max_length=12, validators=[only_digit], unique=True
    )
    phone_number = models.CharField(
        verbose_name='phone number',
        max_length=20, null=True, blank=True
    )
    cdate = models.DateTimeField(
        verbose_name='account create time',
        auto_now_add=True
    )
    mdate = models.DateTimeField(
        verbose_name='account modify time',
        auto_now=True
    )
    email = models.EmailField(
        verbose_name='email address',
        max_length=60, null=True, db_index=True, blank=True
    )
    avatar = models.BinaryField(
        verbose_name='user display avatar',
        null=True, blank=True)
    active = models.BooleanField(default=True, db_index=True)
    admin = models.BooleanField(default=False)  # a superuser
    first_login = models.BooleanField(default=False)

    # notice the absence of a "Password field", that is built in.
    USERNAME_FIELD = USERNAME
    REQUIRED_FIELDS = []  # Username & Password are required by default.

    objects = UserManager()

    def get_full_name(self):
        # The user is identified by their email address
        return self.fullname

    def __str__(self):  # __unicode__ on Python 2
        return self.username

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    class Meta:
        db_table = "user"
