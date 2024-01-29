from django.contrib import admin
from django.urls import path, include

from Itranet.views import dummy_view

from . import views

from account import views as account_views


from .views import (
	# CRUD
	create_post_view,
	create_poll_view,
	create_comment_view,

	update_post_view,
	update_comment_view,
	update_poll_view,
	update_value_view,
	delete_value_view,
	create_poll_value_view,
	my_content_view,

	delete_post_view,
	delete_comment_view,
	delete_poll_view,

	feed_view,
	category_view,
	search_view,

	poll_view,
	post_view,

	select_view,
	like_view,

	set_featured_view,

	)

app_name="blog"

urlpatterns = [

	path('create/post/', create_post_view, name="create_post"),
	path('create/poll/', create_poll_view, name="create_poll"),
	path('create/poll/<int:poll_id>/', create_poll_view, name="create_poll_s2"),
	path('<int:content_id>/comments/create/', create_comment_view, name="add_comment"),


	path('post/<int:post_id>/update/', update_post_view, name="update_post"),
	path('poll/<int:poll_id>/update/', update_poll_view, name="update_poll"),
	path('poll/<int:poll_id>/create_value/', create_poll_value_view, name="create_poll_value"),

	path('poll/<int:poll_id>/<int:value_id>/update/', update_value_view, name="update_value"),
	path('poll/<int:poll_id>/<int:value_id>/delete/', delete_value_view, name="delete_value"),
	path('post/<int:content_id>/<comment_id>/edit/', update_comment_view, name="edit_comment"),

	path('post/<int:post_id>/delete/', delete_post_view, name="delete_post"),
	path('<int:content_id>/<comment_id>/delete/', delete_comment_view, name="delete_comment"),
	path('poll/<int:poll_id>/delete/', delete_poll_view, name="delete_poll"),

	path('post/<int:post_id>/', post_view, name="post"),
	path('poll/<int:poll_id>/', poll_view, name="poll"),

	path('feed/', feed_view, name="feed"),
	path('<str:username>/content/', my_content_view, name="my_content"),
	path('filter/<str:category>/', category_view, name="category"),
	path('search/q/', search_view, name="search"),
	path('poll/select/<int:poll_id>/<int:value_id>/', select_view, name="select"),

	path('like/', like_view, name="like"),
	path('set_featured/', set_featured_view, name="set_featured"),

]