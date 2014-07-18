#coding: utf-8
from django.db import models

from django.contrib.auth.models import User

class Post(models.Model):
    user = models.ForeignKey(User, verbose_name=u'Пользователь')
    title = models.CharField(max_length=256, verbose_name=u'Заголовок')
    text = models.TextField(verbose_name=u'Текст')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'Дата создания')
    updated = models.DateTimeField(auto_now=True, verbose_name=u'Дата изменения')
    is_public = models.BooleanField(default=True, verbose_name=u'Опубликован')

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'Пост'
        verbose_name_plural = u'Посты'

class Comment(models.Model):
    post = models.ForeignKey(Post, verbose_name=u'Пост')
    text = models.TextField(verbose_name=u'Текст')
    user = models.ForeignKey(User, verbose_name=u'Пользователь')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'Дата создания')
    is_public = models.BooleanField(default=True, verbose_name=u'Опубликован')

    def __unicode__(self):
        return u'[{}]: {}'.format(self.user.username, self.text)

    class Meta:
        verbose_name = u'Комментарий'
        verbose_name_plural = u'Комментарии'

class News(models.Model):
    users = models.ManyToManyField(User, verbose_name=u'Пользователи', related_name='abslylikenews')
    title = models.CharField(max_length=256, verbose_name=u'Заголовок')
    link = models.TextField(verbose_name=u'Ссылка')
    desc = models.TextField(verbose_name=u'Краткое описание')
    is_public = models.BooleanField(default=True, verbose_name=u'Опубликован')

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'Новость'
        verbose_name_plural = u'Новости'

class SystemNotification(models.Model):
    title = models.CharField(max_length=256, verbose_name=u'Заголовок')
    text = models.TextField(verbose_name=u'Текст')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'Дата создания')
    is_public = models.BooleanField(default=True, verbose_name=u'Опубликован')

    def get_comments(self):
        return self.comments.order_by('-created')

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'Системное уведомление'
        verbose_name_plural = u'Системные уведомления'

class SystemComment(models.Model):
    notify = models.ForeignKey(SystemNotification, verbose_name=u'Уведомление', related_name='comments')
    text = models.TextField(verbose_name=u'Текст')
    user = models.ForeignKey(User, verbose_name=u'Пользователь')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'Дата создания')
    is_public = models.BooleanField(default=True, verbose_name=u'Опубликован')

    def __unicode__(self):
        return u'[{}]: {}'.format(self.user.username, self.text)

    class Meta:
        verbose_name = u'Комментарий'
        verbose_name_plural = u'Комментарии'
