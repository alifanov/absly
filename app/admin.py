from django.contrib import admin
from app.models import News, NewsGroup, SummaryGroup, SummaryItem

admin.site.register(News)
admin.site.register(NewsGroup)
admin.site.register(SummaryGroup)
admin.site.register(SummaryItem)