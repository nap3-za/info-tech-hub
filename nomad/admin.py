from django.contrib import admin
from .models import Feedback , Question
# Register your models here.

class QuestionAdmin(admin.ModelAdmin):
	list_display = ['author', 'question', 'timestamp', 'is_answered']
	list_filter = []
	search_fields = ['author', 'question', 'timestamp', 'is_answered']
	readonly_fields = ['author', 'question', 'timestamp']

	class Meta:
		model = Question

admin.site.register(Question, QuestionAdmin)


class FeedbackAdmin(admin.ModelAdmin):
    list_filter = []
    list_display = ['author', 'content', 'timestamp', 'feedback']
    search_fields = ['author', 'content', 'timestamp', 'feedback']
    readonly_fields = ['author', 'content', 'timestamp']

    class Meta:
        model = Feedback
admin.site.register(Feedback, FeedbackAdmin)