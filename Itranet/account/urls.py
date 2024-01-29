from django.urls import path
from Itranet.views import dummy_view

from . import views

app_name="account"

urlpatterns = [
	path('setup_account/', views.ProfileSetupView.as_view(), name="setup_profile"),
	path('redirect/', views.redirect_view, name="redirect"),
	path('update_settings/', views.UpdateSettingsView.as_view(), name="update_settings"),
	path('details/<str:subject_username>/', views.DetailsView.as_view(), name="details"),
	path('update/', views.UpdateAccountView.as_view(), name="update"),
	path('delete/', views.DeleteAccountView.as_view(), name="delete"),
	path('search/', views.SearchAccountView.as_view(), name="user_search"),
]