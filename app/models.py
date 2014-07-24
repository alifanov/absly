#coding: utf-8
from django.db import models
from bs4 import BeautifulSoup
from django.core import files
from urlparse import urlparse
import requests
import tempfile
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from bs4 import BeautifulSoup
import requests
import time, json
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from sorl.thumbnail import get_thumbnail
from django.contrib.auth.models import User
from oauth2client.django_orm import FlowField
from oauth2client.django_orm import CredentialsField
from polymorphic import PolymorphicModel
from reportlab.lib.utils import ImageReader

class Snapshot(models.Model):
    project_name = models.CharField(verbose_name=u'Название проекта', blank=True, max_length=256)
    user = models.ForeignKey(User, verbose_name=u'Пользователь', null=True)
    created = models.DateTimeField(auto_now=True, verbose_name=u'Дата создания')
    comment = models.TextField(verbose_name=u'Комментарий')
    hash = models.TextField(blank=True, verbose_name=u'Hash')
    data = models.TextField(verbose_name=u'Данные', blank=True)

    def generate_json(self, user):
        data = {}
        for sg in SummaryGroup.objects.all():
            data[sg.name] = {}
            for si in sg.items.all():
                data[sg.name][si.name] = []
                for block in si.blocks.filter(user=user).all():
                    data[sg.name][si.name].append(block.render())
        self.data = json.dumps(data)
        self.save()

    def __unicode__(self):
        return u'[{}]: {}: {}'.format(self.created, self.user.email, self.comment[:20])

    class Meta:
        verbose_name = u'ES Snapshot'
        verbose_name_plural = u'ES Snapshots'

# Create your models here.
class Project(models.Model):
    is_first = models.BooleanField(default=True, verbose_name=u'First-Time Founder')
    user = models.ForeignKey(User, verbose_name=u'Автор проекта', blank=True, null=True)
    name = models.CharField(max_length=256, verbose_name=u'Название проекта')
    desc = models.TextField(verbose_name=u'Описание проекта')
    site = models.CharField(max_length=256, verbose_name=u'Сайт проекта', blank=True)
    problem = models.TextField(verbose_name=u'Проблема', blank=True)

    def fill_data(self):
        summary_main = SummaryItem.objects.get(name=u'Название')
        summary_name = SummaryTextBlock.objects.create(
            item=summary_main,
            user=self.user,
            text=self.name
        )
        summary_site = SummaryLinkBlock.objects.create(
            item=summary_main,
            user=self.user,
            link=self.site
        )
        summary_desc = SummaryTextBlock.objects.create(
            item=summary_main,
            user=self.user,
            text=self.desc
        )
        summary_main = SummaryItem.objects.get(name=u'Проблема')
        if self.problem:
            summary_problem = SummaryTextBlock.objects.create(
                item=summary_main,
                user=self.user,
                text=self.problem
            )
        block = CanvasBlock.objects.get(name=u'Customer Segments')
        for customer in self.customers.all():
            new_el = CanvasBlockItem.objects.create(
                user=self.user,
                name=customer.name,
                block=block
            )
            pv = CanvasBlockItemParameterValue.objects.get(name=customer.get_type_display())
            pv.elements.add(new_el)

    class Meta:
        verbose_name = u'Проект'
        verbose_name_plural = u'Проекты'

    def __unicode__(self):
        return self.name

CUSTOMER_TYPE = (
    (u'B', u'Бизнес'),
    (u'C', u'Люди'),
    (u'G', u'Государство')
)

class Customer(models.Model):
    name = models.CharField(max_length=256, verbose_name=u'Название')
    type = models.CharField(max_length=1, choices=CUSTOMER_TYPE, verbose_name=u'Тип ЦА')
    project = models.ForeignKey(Project, verbose_name=u'Проект', related_name='customers', null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'ЦА'
        verbose_name_plural = u'ЦА'


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

class GALogData(models.Model):
    user = models.ForeignKey(User, verbose_name=u'Пользователь')
    start_date = models.DateTimeField(verbose_name=u'Начало периода')
    end_date = models.DateTimeField(verbose_name=u'Конец периода')

    a1 = models.IntegerField(default=0, verbose_name=u'Acquisition')
    a2 = models.IntegerField(default=0, verbose_name=u'Activation')
    r1 = models.IntegerField(default=0, verbose_name=u'Retention')
    r2 = models.IntegerField(default=0, verbose_name=u'Referral')
    r3 = models.IntegerField(default=0, verbose_name=u'Revenue')

    def get_start_str(self):
        return self.start_date.strftime('%Y-%m-%d')

    def get_end_str(self):
        return self.end_date.strftime('%Y-%m-%d')

    def get_start_display(self):
        return self.start_date.strftime('%Y.%m.%d')

    def get_end_display(self):
        return self.end_date.strftime('%Y.%m.%d')

    def __unicode__(self):
        return u'Log GA for {}'.format(self.user.username)

    class Meta:
        verbose_name = u'Лог данных из GA'
        verbose_name_plural = u'Логи данных из GA'

class GAFunnelConfig(models.Model):
    user = models.ForeignKey(User, verbose_name=u'Пользователь', related_name='funnel_configs', null=True, blank=True)

    date_range = models.IntegerField(default=1, verbose_name=u'Период отслеживания')
    # start_date = models.CharField(max_length=100, verbose_name=u'Начало периода', blank=True)
    # end_date = models.CharField(max_length=100, verbose_name=u'Конец периода', blank=True)

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

    # activation_value = models.IntegerField(default=0, verbose_name=u'Кол-во пользователей [Activation]')
    # retention_value = models.IntegerField(default=0, verbose_name=u'Кол-во пользователей [Retention]')
    # referral_value = models.IntegerField(default=0, verbose_name=u'Кол-во пользователей [Referral]')
    # revenue_value = models.IntegerField(default=0, verbose_name=u'Кол-во пользователей [Revenue]')

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

    def get_certainly_level(self, user):
        M = self.elements.filter(user=user).count()
        N = 3
        if M:
            lvl = sum([int(el.level) for el in self.elements.filter(user=user)])*100.0/M/N
            return lvl
        else:
            return 0.0

    def is_segment(self):
        return self.name == u'Customer Segments'

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
    user = models.ForeignKey(User, verbose_name=u'Пользователь', null=True, blank=True)
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
    element = models.ForeignKey(CanvasBlockItem, verbose_name=u'Элемент БД', null=True, blank=True,
                                related_name='params')
    block = models.ForeignKey(CanvasBlock, verbose_name=u'Блок БМ', related_name='params')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Параметр'
        verbose_name_plural = u'Параметры'

class CanvasBlockItemParameterValue(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'Значение')
    parameter = models.ForeignKey(CanvasBlockItemParameter, verbose_name=u'Параметр элемента БМ', related_name='values')
    elements = models.ManyToManyField(CanvasBlockItem, verbose_name=u'Элементы', related_name='params_values',
                                      null=True, blank=True    )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Значение параметра'
        verbose_name_plural = u'Значения параметров'

class SummaryGroup(models.Model):
    name = models.CharField(max_length=256, verbose_name=u'Название')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = u'Группы блоков Executive Summary'
        verbose_name = u'Группа блоков Executive Summary'

class SummaryItem(models.Model):
    group = models.ForeignKey(SummaryGroup, verbose_name=u'Группа блоков', related_name='items')

    user = models.ForeignKey(User, verbose_name=u'Пользователь', related_name='summary_items')
    parent = models.ForeignKey('self', verbose_name=u'Parent Item', null=True, blank=True, related_name='childs')
    name = models.CharField(verbose_name=u'Name', max_length=100)
    public = models.BooleanField(default=False, verbose_name=u'Is public data')

    add_text = models.BooleanField(verbose_name=u'Can add text field', default=True)
    add_image = models.BooleanField(verbose_name=u'Can add image field', default=False)
    add_link = models.BooleanField(verbose_name=u'Can add link field', default=False)
    add_linkedin = models.BooleanField(verbose_name=u'Can add linkedIn field', default=False)
    add_angellist = models.BooleanField(verbose_name=u'Can add AngelList field', default=False)
    add_cb = models.BooleanField(verbose_name=u'Can add CrunchBase field', default=False)

    def is_empty_text(self):
        return True and self.text.strip()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'SummaryItem'
        verbose_name_plural = u'SummaryItems'

class SummaryBlock(PolymorphicModel):
    user = models.ForeignKey(User, verbose_name=u'User', null=True, related_name='summary_blocks')
    item = models.ForeignKey(SummaryItem, verbose_name=u'Элемент Executive summary', related_name='blocks')

    def render(self):
        return self.item.name


    def render_to_pdf(self, p, x, y):
        p.drawString(x, y, self.item.name)

class SummaryTextBlock(SummaryBlock):
    text = models.TextField(verbose_name=u'Текст')

    def render(self):
        return render_to_string('summary/text-widget.html', {
            'block': self
        })

    def render_to_pdf(self, p, x, y):
        return self.render()

    def __unicode__(self):
        return u'TextBlock for {}'.format(self.item.name)

    class Meta:
        verbose_name = u'ES TextBlock'
        verbose_name_plural = u'ES TextBlocks'

class SummaryImageBlock(SummaryBlock):
    image = models.ImageField(upload_to=u'upload/', verbose_name=u'Image')

    def render(self):
        return render_to_string('summary/image-widget.html', {
            'block': self
        })

    def render_to_pdf(self):
        return u'<img src="{}" class="es-img" />'.format(self.image.path)

    def __unicode__(self):
        return u'Image #{} for {}'.format(self.pk, self.item.name)

    class Meta:
        verbose_name_plural = u'Images'
        verbose_name = u'Image'

class SummaryLinkBlock(SummaryBlock):
    link = models.TextField(verbose_name=u'Link')
    title = models.CharField(max_length=256, verbose_name=u'Title', blank=True)

    def get_link_title(self):
        return self.title if self.title else self.link

    def render(self):
        return render_to_string('summary/link-widget.html', {
            'block': self
        })

    def render_to_pdf(self):
        return self.render()

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
        return render_to_string('summary/linkedin-widget.html', {
            'block': self
        })

    def render_to_pdf(self):
        return u'<a href="{}" target="_blank"><div class="contact-widget"><img src="{}" /><b>{}</b><p>{}</p></div></a>'\
            .format(self.link, self.avatar.path, self.name, self.desc)

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

class SummaryAngelListBlock(SummaryLinkBlock):
    photo = models.ImageField(upload_to='upload/', verbose_name=u'Photo', blank=True)
    name = models.CharField(max_length=256, verbose_name=u'Name')
    desc = models.TextField(verbose_name='Description')
    startup_id = models.CharField(max_length=256, verbose_name=u'Startup ID for API access')

    def render(self):
        return render_to_string('summary/angel-list-widget.html', {
            'block': self
        })

    def render_to_pdf(self):
        return render_to_string('summary/angel-list-widget.html', {
            'block': self,
            'is_pdf': True
        })

    def save_image_from_url(self, url):
        r = requests.get(url)

        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(r.content)
        img_temp.flush()

        av_name = u'photo_al_{}'.format(time.time()).replace(u'.', u'') + u'.jpg'
        self.photo.save(av_name, File(img_temp), save=False)


    def save(self, *args, **kwargs):
        if not u'http' in self.link: self.link = u'http://'+self.link
        html = requests.get(self.link).text
        soup = BeautifulSoup(html)
        self.startup_id = soup.find('div', attrs={'class': 'startups-show-sections'})['data-id']
        startup_data = requests.get('https://api.angel.co/1/startups/{}'.format(self.startup_id)).json()
        self.name = startup_data['name']
        self.desc = startup_data['product_desc']
        avatar_link = startup_data['logo_url']
        self.save_image_from_url(avatar_link)
        super(SummaryAngelListBlock, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'AngelList block for {}'.format(self.name)

    class Meta:
        verbose_name = 'AngelList block'
        verbose_name_plural = 'AngelList blocks'

class SummaryCrunchBaseBlock(SummaryLinkBlock):
    photo = models.ImageField(upload_to='upload/', verbose_name=u'Photo', blank=True)
    name = models.CharField(max_length=256, verbose_name=u'Name')
    desc = models.TextField(verbose_name='Description')

    def render(self):
        return render_to_string('summary/cb-widget.html', {
            'block': self
        })

    def render_to_pdf(self):
        return render_to_string('summary/cb-widget.html', {
            'block': self,
            'is_pdf': True
        })

    def save_image_from_url(self, url):
        r = requests.get(url)

        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(r.content)
        img_temp.flush()

        av_name = u'photo_cb_{}'.format(time.time()).replace(u'.', u'') + u'.jpg'
        self.photo.save(av_name, File(img_temp), save=False)


    def save(self, *args, **kwargs):
        if not u'http' in self.link: self.link = u'http://'+self.link
        html = requests.get(self.link).text
        soup = BeautifulSoup(html)
        self.name = soup.find('h1').text
        avatar_link = soup.find('img', attrs={'class': 'entity-info-card-primary-image'})['src']
        self.save_image_from_url(avatar_link)
        self.desc = soup.find('div', attrs={'id': 'description'}).text
        super(SummaryCrunchBaseBlock, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'CrunchBase block for {}'.format(self.name)

    class Meta:
        verbose_name = 'CrunchBase block'
        verbose_name_plural = 'CrunchBase blocks'

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