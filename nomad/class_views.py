from django.views import View , generic
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .forms import RegisterForm

from account.models import BaseAccount
from main_asgi.models import Notification, PrivateChatMessage
from nomad.utils import get_create_update_channel

