from django.contrib import admin
from .models import Post, SiteUser, Category, Tags
# Register your models here.


admin.site.register(SiteUser)
admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Tags)