from django.contrib import admin

from blog.models import Comment, Post, Tag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_at')
    list_select_related = ('author',)
    raw_id_fields = ('author',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'published_at')
    list_select_related = ('author', 'post')
    raw_id_fields = ('post', 'author')