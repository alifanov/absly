from django.contrib import admin
from steps.models import *

class RecomendationAdminModel(admin.ModelAdmin):
    class Meta:
        model = Recomentdation
        fieldsets = (
            (None, {'fields':(
                'users', 'title', 'desc', 'target_metrics', 'target_metrics_limit', 'target_metrics_current', 'type'
            )}),
            ('Customer Segments Condition', {
                'fields': ('bmc_customer_segments_hypothesys', 'bmc_customer_segments_facts', 'bmc_customer_segments_actions', 'bmc_customer_segments_money')
            }),
            ('Cost Structure Condition', {
                'fields': ['bmc_cost_structure_hypothesys', 'bmc_cost_structure_facts', 'bmc_cost_structure_actions', 'bmc_cost_structure_money']
            }),
            ('Revenue Streams Condition', {
                'fields': ['bmc_revenue_streams_hypothesys', 'bmc_revenue_streams_facts', 'bmc_revenue_streams_actions', 'bmc_revenue_streams_money']
            }),
            ('Channels Condition', {
                'fields': ['bmc_channels_hypothesys', 'bmc_channels_facts', 'bmc_channels_actions', 'bmc_channels_money']
            }),
            ('Customer Relationship Condition', {
                'fields': ['bmc_customer_relationship_hypothesys', 'bmc_customer_relationship_facts', 'bmc_customer_relationship_actions', 'bmc_customer_relationship_money']
            }),
            ('Value Proposition Condition', {
                'fields': ['bmc_value_proposition_hypothesys', 'bmc_value_proposition_facts', 'bmc_value_proposition_actions', 'bmc_value_proposition_money']
            }),
            ('Key Resources Condition', {
                'fields': ['bmc_key_resources_hypothesys', 'bmc_key_resources_facts', 'bmc_key_resources_actions', 'bmc_key_resources_money']
            }),
            ('Key Activities Condition', {
                'fields': ['bmc_key_activities_hypothesys', 'bmc_key_activities_facts', 'bmc_key_activities_actions', 'bmc_key_activities_money']
            }),
            ('Key Partners Condition', {
                'fields': ['bmc_key_partners_hypothesys', 'bmc_key_partners_facts', 'bmc_key_partners_actions', 'bmc_key_partners_money']
            })
        )

admin.site.register(Task)
admin.site.register(Step)
admin.site.register(Recomentdation, RecomendationAdminModel)