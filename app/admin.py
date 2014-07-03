from django.contrib import admin
from app.models import *

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
    list_display = ['block', 'name', 'user']

admin.site.register(GAFunnelConfig)
admin.site.register(CredentialsModel)
admin.site.register(SummaryTextBlock)
admin.site.register(SummaryImageBlock)
admin.site.register(SummaryLinkBlock)
admin.site.register(SummaryLinkedInBlock)
admin.site.register(News)
admin.site.register(NewsGroup)
admin.site.register(GAProfile)
admin.site.register(SummaryItem)
admin.site.register(CanvasBlock, CanvasBlockAdmin)
admin.site.register(CanvasBlockItem, CanvasBlockItemAdmin)
admin.site.register(CanvasBlockItemParameter, CBPAdminModel)
admin.site.register(CanvasBlockItemParameterValue, CBPVAdmin)