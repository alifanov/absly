from django.contrib import admin
from app.models import News, NewsGroup, SummaryGroup, SummaryItem, CanvasBlock,CanvasBlockItem, CanvasBlockItemParameter,\
CanvasBlockItemParameterValue

class CanvasBlockAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}

class CanvasBlockItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}

admin.site.register(News)
admin.site.register(NewsGroup)
admin.site.register(SummaryGroup)
admin.site.register(SummaryItem)
admin.site.register(CanvasBlock, CanvasBlockAdmin)
admin.site.register(CanvasBlockItem, CanvasBlockItem)
admin.site.register(CanvasBlockItemParameter)
admin.site.register(CanvasBlockItemParameterValue)