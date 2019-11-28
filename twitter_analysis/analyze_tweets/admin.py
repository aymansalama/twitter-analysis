from django.contrib import admin
from .models import Job, Tweet, Keyword

# Register your models here.

admin.site.register(Tweet)
admin.site.register(Keyword)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'start_date', 'end_date', 'user_id')
