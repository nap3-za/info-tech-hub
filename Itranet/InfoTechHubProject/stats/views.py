from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .models import UserAppData, Report, Interactions
from account.models import BaseAccount

from account.utils import get_or_create_appdata

import json

# Create your views here.



@login_required(login_url="login")
def create_report_view(request, *args, **kwargs):
	payload = {}
	auth_user = request.user

	if not auth_user.is_authenticated:
		return redirect('login')

	elif auth_user.is_authenticated:
		auth_user_account = None
		try:
			auth_user_account = BaseAccount.objects.get(id=auth_user.id)
		except:
			payload["response"] = "404"

		if request.POST and request.method == "POST":
			try:
				user_app_data = get_or_create_appdata(auth_user_account, 1)
				subject = request.POST.get("subject")
				subject_id = int(request.POST.get("subject_id"))
				reason = str(request.POST.get("reason"))
				report_reasons = ['Contains sensetive/inappropriate content','Racist', 'False facts']
				subject_choices = ['Account','Post','Poll','Resource','Comment' ]

				if (not reason in report_reasons) or (not subject in subject_choices) or (not int(subject_id) > 0):
					payload["response"] = "Inconsistent data"
				else:
					report = Report.objects.create(subject=subject, subject_id=subject_id, reason=reason)
					report.save()
					user_app_data.reports.add(report)
					user_app_data.save()
					payload["response"] = "Successful"
			except Exception as e:
				print(f"[-] report creation view : {e}")
				payload["response"] = "Inconsistent data"
		else:
			pass
	return HttpResponse(json.dumps(payload), content_type="application/json")
