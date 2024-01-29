from django.contrib import admin

# Register your models here.
from .models import Post, Comment, Poll, PollValue, Content



class ContentAdmin(admin.ModelAdmin):
    list_filter = []
    list_display = ['title', 'kind', 'id']
    search_fields = ['author', 'timestamp', 'title', 'kind']
    readonly_fields = ['kind', 'timestamp']

    class Meta:
        model = Content
admin.site.register(Content, ContentAdmin)


class PostAdmin(admin.ModelAdmin):
    list_filter = []
    list_display = ['id']
    search_fields = ['id']
    readonly_fields = ['id']

    class Meta:
        model = Post
admin.site.register(Post, PostAdmin)

class PollAdmin(admin.ModelAdmin):
    list_filter = []
    list_display = ['id']
    search_fields = ['id']
    readonly_fields = ['id']

    class Meta:
        model = Poll
admin.site.register(Poll, PollAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_filter = []
    list_display = ['author', 'content']
    search_fields = ['author', 'content']
    readonly_fields = ['timestamp']

    ordering = ['-timestamp']

    class Meta:
        model = Comment
admin.site.register(Comment, CommentAdmin)


class PollValueAdmin(admin.ModelAdmin):
    list_filter = []
    list_display = ['poll', 'value', 'id']
    search_fields = ['poll', 'value']
    readonly_fields = []

    class Meta:
        model = PollValue

admin.site.register(PollValue, PollValueAdmin)


