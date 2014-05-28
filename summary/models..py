#coding: utf-8
from django.db import models

class SummaryGroup(models.Model):
    name = models.CharField(verbose_name=u'Name', max_length=100)
    order = models.IntegerField(verbose_name=u'Order', default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'SummaryGroup'
        verbose_name_plural = u'SummaryGroups'


class SummaryItem(models.Model):
    group = models.ForeignKey(SummaryGroup, verbose_name=u'Group')
    name = models.CharField(verbose_name=u'Name', max_length=100)
    text = models.TextField(verbose_name=u'Data')
    public = models.BooleanField(default=False, verbose_name=u'Is public data')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'SummaryItem'
        verbose_name_plural = u'SummaryItems'
