from django.contrib import admin
from .models import Job, Tweet, Keyword

# Register your models here.
admin.site.register(Job)
admin.site.register(Tweet)
admin.site.register(Keyword)