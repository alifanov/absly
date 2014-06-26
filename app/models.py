#coding: utf-8
from django.db import models
from bs4 import BeautifulSoup
from django.core import files
from urlparse import urlparse
import requests
import tempfile
from sorl.thumbnail import get_thumbnail
from django.contrib.auth.models import User
from oauth2client.django_orm import FlowField
from oauth2client.django_orm import CredentialsField

# Create your models here.
class CredentialsModel(models.Model):
    id = models.ForeignKey(User, primary_key=True)
    credential = CredentialsField()

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^oauth2client\.django_orm\.CredentialsField"])

class GAProfile(models.Model):
    profile_id = models.CharField(max_length=256, verbose_name=u'Профиль GA')
    webproperty_id = models.CharField(max_length=256, verbose_name=u'Веб-свойство GA')
    account_id = models.CharField(max_length=256, verbose_name=u'Аккаунт GA')
    user = models.OneToOneField(User, verbose_name=u'Пользователь')

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = u'Настройка GA'
        verbose_name_plural = u'Настройки GA'

class GAFunnelConfig(models.Model):
    user = models.ForeignKey(User, verbose_name=u'Пользователь', related_name='funnel_configs', null=True, blank=True)
    activation_page = models.CharField(max_length=256, verbose_name=u'Страница активации', blank=True)
    activation_event_category = models.CharField(max_length=256, verbose_name=u'Категория события', blank=True)
    activation_event_action = models.CharField(max_length=256, verbose_name=u'Действие события', blank=True)
    activation_event_label = models.CharField(max_length=256, verbose_name=u'Метка события', blank=True)

    retention_page = models.CharField(max_length=256, verbose_name=u'Страница активации', blank=True)
    retention_event_category = models.CharField(max_length=256, verbose_name=u'Категория события', blank=True)
    retention_event_action = models.CharField(max_length=256, verbose_name=u'Действие события', blank=True)
    retention_event_label = models.CharField(max_length=256, verbose_name=u'Метка события', blank=True)

    referral_page = models.CharField(max_length=256, verbose_name=u'Страница активации', blank=True)
    referral_event_category = models.CharField(max_length=256, verbose_name=u'Категория события', blank=True)
    referral_event_action = models.CharField(max_length=256, verbose_name=u'Действие события', blank=True)
    referral_event_label = models.CharField(max_length=256, verbose_name=u'Метка события', blank=True)

    revenue_page = models.CharField(max_length=256, verbose_name=u'Страница активации', blank=True)
    revenue_event_category = models.CharField(max_length=256, verbose_name=u'Категория события', blank=True)
    revenue_event_action = models.CharField(max_length=256, verbose_name=u'Действие события', blank=True)
    revenue_event_label = models.CharField(max_length=256, verbose_name=u'Метка события', blank=True)

    def __unicode__(self):
        return u'{}'.format(self.pk)

    class Meta:
        verbose_name = u'Настройка воронки'
        verbose_name_plural = u'Настройки воронки'

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
    slug = models.CharField(max_length=200, verbose_name=u'Slug', blank=True)
    level = models.CharField(max_length=1, choices=ITEM_LEVEL_CHOICE, verbose_name=u'Уровень определенности', blank=True)
    block = models.ForeignKey(CanvasBlock, verbose_name=u'Блок БМ', related_name='elements')

    segment = models.ForeignKey('self', verbose_name=u'Сегмент клиентов', null=True, blank=True)

    updated_to_1_log = models.TextField(verbose_name=u'Лог при прогрессе статуса на Проверено фактами', blank=True)
    updated_to_2_log = models.TextField(verbose_name=u'Лог при прогрессе статуса на Проверено действиями', blank=True)
    updated_to_3_log = models.TextField(verbose_name=u'Лог при прогрессе статуса на Проверено деньгами', blank=True)

    def is_segment(self):
        return self.block.slug == 'customer-segments'

    def __unicode__(self):
        return u'{} -> {}'.format(self.block.name, self.name)

    class Meta:
        verbose_name = u'Элемент блока БМ'
        verbose_name_plural = u'Элементы блока БМ'

class CanvasBlockItemParameter(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'Параметр элемента БМ')
    element = models.ForeignKey(CanvasBlockItem, verbose_name=u'Элемент БД', null=True, blank=True, related_name='params')
    block = models.ForeignKey(CanvasBlock, verbose_name=u'Блок БМ', related_name='params')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Параметр'
        verbose_name_plural = u'Параметры'

class CanvasBlockItemParameterValue(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'Значение')
    parameter = models.ForeignKey(CanvasBlockItemParameter, verbose_name=u'Параметр элемента БМ', related_name='values')
    elements = models.ManyToManyField(CanvasBlockItem, verbose_name=u'Элементы', related_name='params_values', null=True, blank=True    )

    def __unicode__(self):
        return u'{} -> {}'.format(self.parameter.name, self.name)

    class Meta:
        verbose_name = u'Значение параметра'
        verbose_name_plural = u'Значения параметров'


class SummaryItem(models.Model):
    parent = models.ForeignKey('self', verbose_name=u'Parent Item', null=True, blank=True)
    name = models.CharField(verbose_name=u'Name', max_length=100)
    public = models.BooleanField(default=False, verbose_name=u'Is public data')

    add_text = models.BooleanField(verbose_name=u'Can add text field', default=True)
    add_image = models.BooleanField(verbose_name=u'Can add image field', default=False)
    add_link = models.BooleanField(verbose_name=u'Can add link field', default=False)
    add_linkedin = models.BooleanField(verbose_name=u'Can add linkedIn field', default=False)

    def is_empty_text(self):
        return True and self.text.strip()

    def __unicode__(self):
        return u'{} -> {}'.format(self.group.name, self.name)

    class Meta:
        verbose_name = u'SummaryItem'
        verbose_name_plural = u'SummaryItems'


class SummaryBlock(models.Model):
    item = models.ForeignKey(SummaryItem, verbose_name=u'Элемент Executive summary')

class SummaryTextBlock(SummaryBlock):
    text = models.TextField(verbose_name=u'Текст')

    def __unicode__(self):
        return u'TextBlock for {}'.format(self.item.name)

    class Meta:
        verbose_name = u'ES TextBlock'
        verbose_name_plural = u'ES TextBlocks'

class SummaryImageBlock(SummaryBlock):
    image = models.ImageField(upload_to='upload/', verbose_name=u'Image')

    def __unicode__(self):
        return 'Image #{} for {}'.format(self.pk, self.item.name)

    class Meta:
        verbose_name_plural = 'Images'
        verbose_name = 'Image'

class SummaryLinkBlock(SummaryBlock):
    link = models.TextField(verbose_name=u'Link')

    def __unicode__(self):
        return 'Link for {}'.format(self.item.name)

    class Meta:
        verbose_name = 'Link'
        verbose_name_plural = 'Links'

class SummaryLinkedInBlock(SummaryLinkBlock):
    avatar = models.ImageField(upload_to='upload/', verbose_name=u'Avatar')
    name = models.CharField(max_length=256, verbose_name=u'Name')
    desc = models.TextField(verbose_name='Description')

    def __unicode__(self):
        return 'LinkedIn for {}'.format(self.name)

    class Meta:
        verbose_name = 'LinkedIn link'
        verbose_name_plural = 'LinkedIn links'

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