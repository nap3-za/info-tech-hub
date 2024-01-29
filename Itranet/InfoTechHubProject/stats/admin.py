from django.contrib import admin
from .models import UserAppData

# Register your models here.
class UserAppDataAdmin(admin.ModelAdmin):
	list_display = ('user',)
	search_fields = ('user',)
	readonly_fields=('reports', 'positive_responses', 'negative_responses', 'question_count', 'feedback_count', 'content_count', 'Interactions')
	filter_horizontal = ()
	list_filter = ()
	fieldsets = ()

admin.site.register(UserAppData, UserAppDataAdmin)