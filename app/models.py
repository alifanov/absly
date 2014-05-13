#coding: utf-8
from django.db import models

# Create your models here.

class NewsGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'Название группы')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Группа новостей'
        verbose_name_plural = u'Группы новостей'

class News(models.Model):
    link = models.TextField(verbose_name=u'Ссылка на новость')
    title = models.CharField(max_length=100, verbose_name=u'Заголовок')
    description = models.TextField(verbose_name=u'Описание')
    created = models.DateTimeField(verbose_name=u'Дата создания', auto_now=True)
    photo = models.ImageField(upload_to='uploads/', verbose_name=u'Фотография статьи')

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'Новость'
        verbose_name_plural = u'Новости'