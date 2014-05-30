from django.contrib import admin
from app.models import News, NewsGroup, SummaryGroup, SummaryItem, CanvasBlock,CanvasBlockItem, CanvasBlockItemParameter,\
CanvasBlockItemParameterValue

admin.site.register(News)
admin.site.register(NewsGroup)
admin.site.register(SummaryGroup)
admin.site.register(SummaryItem)
admin.site.register(CanvasBlock)
admin.site.register(CanvasBlockItem)
admin.site.register(CanvasBlockItemParameter)
admin.site.register(CanvasBlockItemParameterValue)