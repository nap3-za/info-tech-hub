
from django.urls import path
from .views import (
	create_resource_view,
	update_resource_view,
	resource_view,
	resources_view,
	crop_image_view,
	news_view,
	send_question_view,
	send_feedback_view,
	questions_view,
	del_question_view,
	clear_questions_view,
)
app_name = "feature"

urlpatterns = [
	path('resources/', resources_view, name="res_browse"),
	path('create_resource/', create_resource_view, name="res_create"),
	path('update_resource/<int:resource_id>/', update_resource_view, name="res_update"),
	path('resource/<int:resource_id>/', resource_view, name="res_details"),
	path('resource/<int:resource_id>/edit/cropImage/', crop_image_view, name="crop_image"),
	path('latest_tech_news/', news_view, name="news"),
	path('send_a_question/', send_question_view, name="send_question"),
	path('send_feedback/', send_feedback_view, name="send_feedback"),
	path('questions/', questions_view, name="questions"),
	path('questions/<int:question_id>/delete/', del_question_view, name="question_del"),
	path('clear_questions/', clear_questions_view, name="clear_questions"),
]

