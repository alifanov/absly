from django.contrib import admin
from talk.models import *

class NewsAdmin(admin.ModelAdmin):
    filter_horizontal = ('users',)

admin.site.register(SystemNotification)
admin.site.register(SystemComment)
admin.site.register(News, NewsAdmin)
admin.site.register(Post)
admin.site.register(Comment)