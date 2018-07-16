from django.contrib import admin
from jhin import models

# Register your models here.

admin.site.register(models.UserInfo)
admin.site.register(models.Article)
admin.site.register(models.ArticleJTag)
admin.site.register(models.ArticleUpDown)
admin.site.register(models.Category)
admin.site.register(models.Tag)
admin.site.register(models.Blog)
admin.site.register(models.Comment)
