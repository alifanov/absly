#coding: utf-8
from django.db import models
from bs4 import BeautifulSoup
from django.core import files
import requests
import tempfile
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
    title = models.CharField(max_length=100, verbose_name=u'Заголовок', blank=True)
    description = models.TextField(verbose_name=u'Описание', blank=True)
    created = models.DateTimeField(verbose_name=u'Дата создания', auto_now=True)
    photo = models.ImageField(upload_to='uploads/', verbose_name=u'Фотография статьи', blank=True)

    def save(self, *args, **kwargs):
        r = requests.get(self.link)
        if r.status_code == 200 and r.text:
            soup = BeautifulSoup(r.text)
            self.title = soup.title.string
            self.description = soup.get_text()[:200]
            img = soup.find('img')
            if img:
                if not u'mc.yandex' in img['src']:
                    self.photo = self.save_image_from_url(soup.find('img')['src'])
        super(News, self).save(*args, **kwargs)

    def save_image_from_url(self, url):
        r = requests.get(url)
        if r.status_code != r.codes.ok:
            return
        fname = url.split('/')[-1]
        lf = tempfile.NamedTemporaryFile()

        for block in r.iter_content(1024*8):
            if not block: break
            lf.write(block)

        self.photo.save(fname, files.File(lf))

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'Новость'
        verbose_name_plural = u'Новости'