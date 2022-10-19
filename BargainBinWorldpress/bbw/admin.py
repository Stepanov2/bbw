from django.contrib import admin
from .models import Post, SiteUser, Category, Tags
# Register your models here.


def give_author(modeladmin, request, queryset):  # request — объект хранящий информацию о
    # запросе и queryset — грубо говоря набор объектов, которых мы выделили галочками.
    # print(request.GET)
    # print(request.POST)
    queryset.update(is_author=True)


give_author.short_description = 'Сделать автором'


def revoke_author(modeladmin, request, queryset):

    queryset.update(is_author=False)


revoke_author.short_description = 'Отозвать статус автора'


class TagsAdminInline(admin.TabularInline):
    model = Post.tags.through
    extra = 1

@admin.register(SiteUser)
class SiteUserAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    list_display = ('pk', 'display_username',
                    'is_author', 'is_editor', 'can_publish', 'is_admin', 'is_moderator',
                    'date_registered')
    list_editable = ('is_author', 'is_editor', 'can_publish', 'is_admin', 'is_moderator')
    search_fields = ('display_username', 'user__email')
    actions = [give_author, revoke_author]
    list_display_links = ('display_username',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    list_display = ('pk', 'title', 'is_article',
                    'author', 'published', 'publication_date')
    list_editable = ('published', 'publication_date')
    list_filter = ('published', 'is_article', 'author')
    list_display_links = ('title',)
    search_fields = ('title', 'content')
    inlines = (TagsAdminInline,)


# admin.site.register(SiteUser, SiteUserAdmin)
# admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Tags)
