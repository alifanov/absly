#coding: utf-8
from django.db import models
from bs4 import BeautifulSoup
from django.core import files
from urlparse import urlparse
import requests
import tempfile
from django.contrib.sites.models import Site

from bs4 import BeautifulSoup
import requests
import time
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from sorl.thumbnail import get_thumbnail
from django.contrib.auth.models import User
from oauth2client.django_orm import FlowField
from oauth2client.django_orm import CredentialsField
from polymorphic import PolymorphicModel
from reportlab.lib.utils import ImageReader

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

    date_range = models.IntegerField(default=1, verbose_name=u'Период отслеживания')
    start_date = models.CharField(max_length=100, verbose_name=u'Начало периода', blank=True)
    end_date = models.CharField(max_length=100, verbose_name=u'Конец периода', blank=True)

    user_sum = models.FloatField(default=0.0, verbose_name=u'Стоимость пользователя')

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

    activation_value = models.IntegerField(default=0, verbose_name=u'Кол-во пользователей [Activation]')
    retention_value = models.IntegerField(default=0, verbose_name=u'Кол-во пользователей [Retention]')
    referral_value = models.IntegerField(default=0, verbose_name=u'Кол-во пользователей [Referral]')
    revenue_value = models.IntegerField(default=0, verbose_name=u'Кол-во пользователей [Revenue]')

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
    level = models.CharField(max_length=1, choices=ITEM_LEVEL_CHOICE, verbose_name=u'Уровень определенности', default='0')
    block = models.ForeignKey(CanvasBlock, verbose_name=u'Блок БМ', related_name='elements')

    segment = models.ForeignKey('self', verbose_name=u'Сегмент клиентов', null=True, blank=True)

    def get_logs(self):
        return self.logs.order_by('created')
    def is_segment(self):
        return not self.segment

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Элемент блока БМ'
        verbose_name_plural = u'Элементы блока БМ'

class CanvasLogEntry(models.Model):
    old_value = models.CharField(max_length=1, choices=ITEM_LEVEL_CHOICE, verbose_name=u'Старое значение', default='0')
    new_value = models.CharField(max_length=1, choices=ITEM_LEVEL_CHOICE, verbose_name=u'Новое значение', default='0')
    text = models.TextField(blank=True, verbose_name=u'Текст')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'Дата создания')
    element = models.ForeignKey(CanvasBlockItem, verbose_name=u'Элемент БМ', related_name='logs')

    def __unicode__(self):
        return u'Canvas Log Entry #{}'.format(self.pk)

    class Meta:
        verbose_name = u'Лог'
        verbose_name_plural = u'Логи'


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
        return self.name

    class Meta:
        verbose_name = u'Значение параметра'
        verbose_name_plural = u'Значения параметров'


class SummaryItem(models.Model):
    user = models.ForeignKey(User, verbose_name=u'Пользователь', related_name='summary_items')
    parent = models.ForeignKey('self', verbose_name=u'Parent Item', null=True, blank=True, related_name='childs')
    name = models.CharField(verbose_name=u'Name', max_length=100)
    public = models.BooleanField(default=False, verbose_name=u'Is public data')

    add_text = models.BooleanField(verbose_name=u'Can add text field', default=True)
    add_image = models.BooleanField(verbose_name=u'Can add image field', default=False)
    add_link = models.BooleanField(verbose_name=u'Can add link field', default=False)
    add_linkedin = models.BooleanField(verbose_name=u'Can add linkedIn field', default=False)

    def is_empty_text(self):
        return True and self.text.strip()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'SummaryItem'
        verbose_name_plural = u'SummaryItems'

class SummaryBlock(PolymorphicModel):
    user = models.ForeignKey(User, verbose_name=u'User', null=True)
    item = models.ForeignKey(SummaryItem, verbose_name=u'Элемент Executive summary', related_name='blocks')

    def render(self):
        return self.item.name

    def render_to_pdf(self, p, x, y):
        p.drawString(x, y, self.item.name)

class SummaryTextBlock(SummaryBlock):
    text = models.TextField(verbose_name=u'Текст')

    def render(self):
        return self.text

    def render_to_pdf(self, p, x, y):
        p.drawString(x, y, self.text)

    def __unicode__(self):
        return u'TextBlock for {}'.format(self.item.name)

    class Meta:
        verbose_name = u'ES TextBlock'
        verbose_name_plural = u'ES TextBlocks'

class SummaryImageBlock(SummaryBlock):
    image = models.ImageField(upload_to=u'upload/', verbose_name=u'Image')

    def render(self):
        return u'<img src="{}" class="es-img" />'.format(self.image.url)

    def render_to_pdf(self, p, x, y):
        p.drawImage(self.image.path, x, y, height=100)

    def __unicode__(self):
        return u'Image #{} for {}'.format(self.pk, self.item.name)

    class Meta:
        verbose_name_plural = u'Images'
        verbose_name = u'Image'

class SummaryLinkBlock(SummaryBlock):
    link = models.TextField(verbose_name=u'Link')
    title = models.CharField(max_length=256, verbose_name=u'Title', blank=True)

    def render(self):
        return u'<a href="{}">{}</a>'.format(self.link, self.title)

    def render_to_pdf(self, p, x, y):
        p.drawString(x, y, self.link)

    def __unicode__(self):
        return u'Link for {}'.format(self.item.name)

    class Meta:
        verbose_name = u'Link'
        verbose_name_plural = u'Links'



class SummaryLinkedInBlock(SummaryLinkBlock):
    avatar = models.ImageField(upload_to='upload/', verbose_name=u'Avatar', blank=True)
    name = models.CharField(max_length=256, verbose_name=u'Name')
    desc = models.TextField(verbose_name='Description')

    def render(self):
        return u'<div class="contact-widget"><img src="{}" /><b>{}</b><p>{}</p></div>'.format(self.avatar.url, self.name, self.desc)

    def render_to_pdf(self, p, x, y):
        p.drawImage(self.avatar.path, x, y)

    def save_image_from_url(self, url):
        r = requests.get(url)

        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(r.content)
        img_temp.flush()

        av_name = u'avatar_linkedin_{}'.format(time.time()).replace(u'.', u'') + u'.jpg'
        self.avatar.save(av_name, File(img_temp), save=False)


    def save(self, *args, **kwargs):
        if not u'http' in self.link: self.link = u'http://'+self.link
        html = requests.get(self.link).text
        soup = BeautifulSoup(html)
        self.name = soup.find('span', attrs={'class': 'full-name'}).text
        avatar_link = soup.find('img', attrs={'class': 'photo'})['src']
        self.desc = soup.find('p', attrs={'class': 'headline-title'}).text
        self.save_image_from_url(avatar_link)
        super(SummaryLinkedInBlock, self).save(*args, **kwargs)

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