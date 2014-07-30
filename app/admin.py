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
    list_display = ['name', 'block', 'user']

class SummaryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'group']

class GAFunnelConfigAdminModel(admin.ModelAdmin):
    list_display = ('id', 'user')

admin.site.register(Snapshot)
admin.site.register(GALogData)
admin.site.register(GAFunnelConfig, GAFunnelConfigAdminModel)
admin.site.register(CredentialsModel)
admin.site.register(SummaryTextBlock)
admin.site.register(SummaryImageBlock)
admin.site.register(SummaryLinkBlock)
admin.site.register(SummaryLinkedInBlock)
admin.site.register(SummaryAngelListBlock)
admin.site.register(SummaryCrunchBaseBlock)
admin.site.register(SummaryMarketBlock)
admin.site.register(SummaryInvestmentRequestBlock)
admin.site.register(Customer)
admin.site.register(Project)
admin.site.register(GAProfile)
admin.site.register(SummaryGroup)
admin.site.register(SummaryItem, SummaryItemAdmin)
admin.site.register(CanvasBlock, CanvasBlockAdmin)
admin.site.register(CanvasBlockItem, CanvasBlockItemAdmin)
admin.site.register(CanvasBlockItemParameter, CBPAdminModel)
admin.site.register(CanvasBlockItemParameterValue, CBPVAdmin)