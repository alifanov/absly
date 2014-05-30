#coding: utf-8
from django.db import models
from bs4 import BeautifulSoup
from django.core import files
from urlparse import urlparse
import requests
import tempfile
from sorl.thumbnail import get_thumbnail
from django.contrib.auth.models import User
# Create your models here.

class CanvasBlock(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'Название блока')
    slug = models.CharField(max_length=200, verbose_name=u'Slug')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Блок шаблона бизнес-модели'
        verbose_name_plural = u'Блоки шаблона бизнес-модели'


ITEM_LEVEL_CHOICE = (
    ('0', u'Гипотеза'),
    ('1', u'Исследование'),
    ('2', u'Проверено фактами'),
    ('3', u'Проверено деньгами')
)

class CanvasBlockItem(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'Название элемента')
    slug = models.CharField(max_length=200, verbose_name=u'Slug')
    level = models.CharField(max_length=1, choices=ITEM_LEVEL_CHOICE, verbose_name=u'Уровень определенности')
    block = models.ForeignKey(CanvasBlock, verbose_name=u'Блок БМ', related_name='elements')

    def is_segment(self):
        return self.block.slug == 'customer-development'

    def __unicode__(self):
        return u'{} -> {}'.format(self.block.name, self.name)

    class Meta:
        verbose_name = u'Элемент блока БМ'
        verbose_name_plural = u'Элементы блока БМ'

class CanvasBlockItemParameter(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'Параметр элемента БМ')
    element = models.ForeignKey(CanvasBlockItem, verbose_name=u'Элемент БД')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Параметр'
        verbose_name_plural = u'Параметры'

class CanvasBlockItemParameterValue(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'Значение')
    parameter = models.ForeignKey(CanvasBlockItemParameter, verbose_name=u'Параметр элемента БМ')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Значение параметра'
        verbose_name_plural = u'Значения параметров'


class SummaryGroup(models.Model):
    name = models.CharField(verbose_name=u'Name', max_length=100)
    order = models.IntegerField(verbose_name=u'Order', default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'SummaryGroup'
        verbose_name_plural = u'SummaryGroups'


class SummaryItem(models.Model):
    group = models.ForeignKey(SummaryGroup, verbose_name=u'Group', related_name='items')
    name = models.CharField(verbose_name=u'Name', max_length=100)
    text = models.TextField(verbose_name=u'Data')
    public = models.BooleanField(default=False, verbose_name=u'Is public data')

    def is_empty_text(self):
        return True and self.text.strip()

    def __unicode__(self):
        return u'{} -> {}'.format(self.group.name, self.name)

    class Meta:
        verbose_name = u'SummaryItem'
        verbose_name_plural = u'SummaryItems'


class NewsGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'Название группы')
    users = models.ManyToManyField(User, verbose_name=u'Пользователи', related_name='news_groups')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Группа новостей'
        verbose_name_plural = u'Группы новостей'

class News(models.Model):
    link = models.TextField(verbose_name=u'Ссылка на новость')
    title = models.CharField(max_length=512, verbose_name=u'Заголовок', blank=True)
    description = models.TextField(verbose_name=u'Описание', blank=True)
    created = models.DateTimeField(verbose_name=u'Дата создания', auto_now=True)
    photo = models.ImageField(upload_to='uploads/', verbose_name=u'Фотография статьи', blank=True)
    group = models.ForeignKey(NewsGroup, verbose_name=u'Группа новостей', null=True, related_name='news')
    users = models.ManyToManyField(User, verbose_name=u'Пользователи', related_name='news')

    def save(self, *args, **kwargs):
        if not self.title:
            r = requests.get(self.link)
            if r.status_code == 200 and r.text:
                soup = BeautifulSoup(r.text)
                self.title = soup.title.string.encode('utf-8')
                self.description = soup.find('meta', {'name': 'description'})['content']
                for img in soup.findAll('img'):
                    if img:
                        nn = img['src']
                        if not u'mc.yandex' in nn:
                            img_url = nn
                            if nn[0] == u'/':
                                u = urlparse(self.link)
                                img_url = u'{}://{}{}'.format(u.scheme, u.netloc, nn)
                            self.save_image_from_url(img_url)
                            break
        super(News, self).save(*args, **kwargs)

    def save_image_from_url(self, url):
        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            return
        fname = url.split('/')[-1]
        lf = tempfile.NamedTemporaryFile()


        for block in r.iter_content():
            if not block: break
            lf.write(block)
        lf.flush()
        self.photo.save(fname, files.File(lf))

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'Новость'
        verbose_name_plural = u'Новости'