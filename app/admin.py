from django.contrib import admin
from app.models import News, NewsGroup, SummaryGroup, SummaryItem, CanvasBlock,CanvasBlockItem, CanvasBlockItemParameter,\
CanvasBlockItemParameterValue, CredentialsModel

class CBPVAdmin(admin.ModelAdmin):
    model = CanvasBlockItemParameterValue
    filter_horizontal = ['elements']

class CBPVInline(admin.TabularInline):
    model = CanvasBlockItemParameterValue

class CBPAdminModel(admin.ModelAdmin):
    model = CanvasBlockItemParameter
    inlines = [CBPVInline]
    list_display = ['name', 'block']

class CanvasBlockAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}

class CanvasBlockItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}

admin.site.register(CredentialsModel)
admin.site.register(News)
admin.site.register(NewsGroup)
admin.site.register(SummaryGroup)
admin.site.register(SummaryItem)
admin.site.register(CanvasBlock, CanvasBlockAdmin)
admin.site.register(CanvasBlockItem, CanvasBlockItemAdmin)
admin.site.register(CanvasBlockItemParameter, CBPAdminModel)
admin.site.register(CanvasBlockItemParameterValue, CBPVAdmin)