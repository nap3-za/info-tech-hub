from django.contrib.auth.decorators import login_required
from nomad.utils import get_create_update_channel

"""
View scafolding
"""
@login_required(login_url="login")
def view(request, *args, **kwargs):
	context = {}
	auth_user = request.user

	if not auth_user.is_authenticated:
		return redirect('login')

	elif auth_user.is_authenticated:
		auth_user_account = None
		try:
			auth_user_account = BaseAccount.objects.get(id=auth_user.id)
		except:
			return redirect("error", code=404)


	context["con_general"] = True
	channel = get_create_update_channel(user=auth_user_account, view="home")
	context["channel"] = channel
	return render(request, "", context)



"""
Class based / Generic views
"""
class IndexView(generic.ListView):
	template_name = 'polls/index.html'
	context_object_name = 'latest_question_list'

	def get_queryset(self):
		"""Return the last five published questions."""
		return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
	model = Question
	template_name = 'polls/detail.html'

class ResultsView(generic.DetailView):
	model = Question
	template_name = 'polls/results.html'


def vote(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	try:
		selected_choice = question.choice_set.get(pk=request.POST['choice'])
	
	except (KeyError, Choice.DoesNotExist):
	# Redisplay the question voting form.
		return render(request, 'polls/detail.html', {
		'question': question,
		'error_message': "You didn't select a choice.",
		})
	else:
		selected_choice.votes  = F('votes') + 1
		selected_choice.save()
		# Always return an HttpResponseRedirect after successfully dealing
		# with POST data. This prevents data from being posted twice if a
		# user hits the Back button.
		return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))






"""

Lessons

> get_object/list_or_404
> F('') + 1 ( avoids race conditions )
> pluralize on the backend
> static/app_name/*
"""


