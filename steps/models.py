#coding: utf-8
from django.db import models
from app.models import CanvasBlockItem
from django.contrib.auth.models import User
from datetime import datetime
from django.utils.timezone import utc

STEP_TYPE = (
    (u'C', u'Customer'),
    (u'P', u'Product'),
    (u'F', u'Fundrising')
)
class Step(models.Model):
    user = models.ForeignKey(User, verbose_name=u'Пользователь', related_name='steps', null=True, blank=True)
    title = models.CharField(max_length=256, verbose_name=u'Название')
    desc = models.TextField(verbose_name=u'Описание', blank=True)
    deadline = models.DateTimeField(verbose_name=u'DeadLine', blank=True, null=True)
    type = models.CharField(max_length=1, choices=STEP_TYPE, verbose_name=u'Тип шага')
    element = models.ForeignKey(CanvasBlockItem, verbose_name=u'Элемент блока бизнес-модели')
    status = models.BooleanField(default=False, verbose_name=u'Выполнена')
    # target_custom = models.CharField(max_length=256, verbose_name=u'Абстрактная цель', blank=True)
    target_metrics = models.CharField(max_length=256, verbose_name=u'Цель по метрике', blank=True)
    target_metrics_limit = models.IntegerField(default=0, verbose_name=u'Уровень цели по метрике')
    target_metrics_current = models.IntegerField(default=0, verbose_name=u'Текущее значение по цели')
    done_log = models.TextField(verbose_name=u'Комментарий к завершению шага', blank=True)
    delete_log = models.TextField(verbose_name=u'Комментарий к удалению шага', blank=True)
    removed = models.BooleanField(default=False, verbose_name=u'Удален')

    def get_deadline_last(self):
        if self.deadline is not None:
            now = datetime.utcnow().replace(tzinfo=utc)
            return (self.deadline - now).days
        return u''

    def is_clear_deadline(self):
        if self.deadline and self.get_deadline_last() < 7:
            return True
        return False

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'Шаг'
        verbose_name_plural = u'Шаги'


class Recomentdation(models.Model):
    users = models.ManyToManyField(User, verbose_name=u'Пользователи', related_name='recomendations')
    title = models.CharField(max_length=256, verbose_name=u'Название')
    desc = models.TextField(verbose_name=u'Описание')
    target_custom = models.CharField(max_length=256, verbose_name=u'Абстрактная цель', blank=True)
    target_metrics = models.CharField(max_length=256, verbose_name=u'Цель по метрике', blank=True)
    target_metrics_limit = models.IntegerField(default=0, verbose_name=u'Уровень цели по метрике')
    type = models.CharField(max_length=1, choices=STEP_TYPE, verbose_name=u'Тип шага')
    element = models.ForeignKey(CanvasBlockItem, verbose_name=u'Элемент блока бизнес-модели')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'Время создания')

    def create_step(self, user):
        s = Step.objects.create(
            user=user,
            title=self.title,
            desc=self.desc,
            type=self.type,
            element=self.element,
            target_custom=self.target_custom,
            target_metrics=self.target_metrics,
            target_metrics_limit=self.target_metrics_limit
        )
        return s

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'Рекомендация'
        verbose_name_plural = u'Рекомендации'


class Task(models.Model):
    title = models.CharField(max_length=256, verbose_name=u'Название задачи')
    done = models.BooleanField(verbose_name=u'Выполнена', default=False)
    step = models.ForeignKey(Step, verbose_name=u'Шаг', related_name='subtasks')

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name_plural = u'Задачи'
        verbose_name = u'Задача'
