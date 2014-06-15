from django.contrib import admin
from app.models import News, NewsGroup, SummaryGroup, SummaryItem, CanvasBlock,CanvasBlockItem, CanvasBlockItemParameter,\
CanvasBlockItemParameterValue

class CanvasBlockParameterValueInline(admin.TabularInline):
    model = CanvasBlockItemParameterValue

class CanvasBlockParameterInline(admin.TabularInline):
    model = CanvasBlockItemParameter
    inlines = [CanvasBlockParameterValueInline]

class CanvasBlockAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}

class CanvasBlockItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}
    inlines = [CanvasBlockParameterInline]

admin.site.register(News)
admin.site.register(NewsGroup)
admin.site.register(SummaryGroup)
admin.site.register(SummaryItem)
admin.site.register(CanvasBlock, CanvasBlockAdmin)
admin.site.register(CanvasBlockItem, CanvasBlockItemAdmin)
admin.site.register(CanvasBlockItemParameter)
admin.site.register(CanvasBlockItemParameterValue)