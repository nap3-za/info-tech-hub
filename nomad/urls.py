from django.urls import path
from .views import (
	send_question_view,
	send_feedback_view,
	questions_view,
	del_question_view,
	clear_questions_view,
)



app_name = "nomad"

urlpatterns = [
	path('send_a_question/', send_question_view, name="send_question"),
	path('send_feedback/', send_feedback_view, name="send_feedback"),
	path('questions/', questions_view, name="questions"),
	path('questions/<int:question_id>/delete/', del_question_view, name="question_del"),
	path('clear_questions/', clear_questions_view, name="clear_questions"),
]