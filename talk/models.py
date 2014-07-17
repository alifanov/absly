#coding: utf-8
from django.db import models

from django.contrib.auth.models import User

class Post(models.Model):
    user = models.ForeignKey(User, verbose_name=u'Пользователь')
    title = models.CharField(max_length=256, verbose_name=u'Заголовок')