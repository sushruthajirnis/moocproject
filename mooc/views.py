from django.shortcuts import render
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf
from django.template import RequestContext  
from django.contrib.auth.models import User
from mooc.models import Mooc
import requests
import json

# Create your views here.
all_moocs = None
selected_mooc = None
headers = {'content-type': 'application/json', 'charset': 'utf-8'}
act_usr={}
def login_user(request):
	global all_moocs
	all_moocs= Mooc.objects.all()
	state = "Please log in below !!!"

	username = password = ''
	if request.POST:
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				state = "You're successfully logged in!"
			else:
				state = "Your account is not active, please contact the site admin."
		else:
			state = "Your username and/or password were incorrect."

	return render_to_response('login.html',{'state':state, 'username': username},RequestContext(request, {}))

def add_user(request):
	
	fname = request.POST.get('fname')
	lname = request.POST.get('lname')
	email = request.POST.get('email')
	password = request.POST.get('password')
    
	if User.objects.filter(username=email).count():
		state = "Account already exists!"
		return render_to_response('signup.html', {'state':state}, RequestContext(request, {}))
	
	if(email is not None):
		user = User.objects.create_user(email,email,password)
		user.first_name = fname
		user.last_name = lname
		user.save()
		state = "Account created!"
		payload={"email":email,"quizzes":[],"own":[],"enrolled":[]}
		tempUrl="http://localhost:8080/user"
		response = requests.post(tempUrl, data=json.dumps(payload), headers=headers)
		
		return render_to_response('login.html', {'state':state}, RequestContext(request, {}))
	
	state = "All fields are mandatory!!!"
	return render_to_response('signup.html', {'state':state}, RequestContext(request, {}))
#all methods have default
#def get_html(): to render html data (get context)
#def profile_page()
#def update_user()
#def list_category()
	
	
