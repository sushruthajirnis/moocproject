from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login ,logout
from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf
from django.template import RequestContext  
from django.contrib.auth.models import User
from mooc.models import Mooc
import requests
import json
import urllib2

# Create your views here.
all_moocs = None
selected_mooc = None
headers = {'content-type': 'application/json', 'charset': 'utf-8'}


def setMooc():
	global all_moocs,selected_mooc
	all_moocs=Mooc.objects.all()
	for mooc in all_moocs:
		if mooc.default:
			
			selected_mooc=mooc
			
	return

def loginUser(request):
	global selected_mooc, all_moocs
	setMooc()
	str(selected_mooc)
	#global all_moocs
	#all_moocs= Mooc.objects.all()
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
				if (request.session.has_key(user.username)):
					del request.session[user.username]
					
				request.session[user.username]={"url":selected_mooc.primaryUrl,"mooc":{"id":selected_mooc.id,"name":selected_mooc.groupName}}
				
				return render_to_response('home.html',{},RequestContext(request))
			else:
				state = "Your account is not active, please contact the site admin."
		else:
			state = "Your username and/or password were incorrect."
  	
	return render_to_response('login.html',{'state':state, 'username': username},RequestContext(request, {}))

def createCourse(request):
	return render_to_response('createCourse.html', RequestContext(request, {}))
			
def addUser(request):
	print "inside add user"
	global selected_mooc, all_moocs, headers
	setMooc()
	fname = request.POST.get('fname')
	lname = request.POST.get('lname')
	email = request.POST.get('email')
	password = request.POST.get('password')
    
	if User.objects.filter(username=email).count():
		state = "Account already exists!"
		print "here"
		return render_to_response('login.html', {'state':state}, RequestContext(request, {}))
	
	
	if(email is not None):
		user = User.objects.create_user(email,email,password)
		user.first_name = fname
		user.last_name = lname
		user.save()
		print "saved in sqlite"
		state = "Account created!"
		payload={"email":email,"quizzes":[],"own":[],"enrolled":[]}
		
		reqUrl = "http://localhost:8080" +"/user"
		#req=urllib2.Request(reqUrl,payload,headers)
		#response=urllib2.urlopen(req).read()
		response = requests.post(reqUrl, data=json.dumps(payload), headers=headers)
		
		return render_to_response('login.html', {'state':state}, RequestContext(request, {}))
	
	state = "All fields are mandatory!!!"
	return render_to_response('home.html', {'state':state}, RequestContext(request, {}))

			
#all methods have default
#def get_html(): to render html data (get context)
#def profile_page()
#def update_user()
#def list_category()
#def add_category()
#working

 

def loginPage(request):
	setMooc()
	return redirect('/')

def getRenderJson(request):
	global all_moocs, selected_mooc
	jsondata["email":request.user.username]
	jsondata [""]
	return jsondata

def userLogout(request):
	global selected_mooc, all_moocs, headers
	try:
		del request.session[request.user.username]
	except KeyError:
		pass		
	logout(request)
	return loginPage(request)

def enrollCourse(request):
	#takes place in the context of a logged in user
	# for enrolling we need to confirm 
	#1. He is registered User(username in sqlite) -- not required 
	#2 	He can register in the course added by him
	#3 	He must not be already enrolled
	#4  Enrolling means his data in mongo is updated
	global selected_mooc, headers
	
	print "here in enroll course"
	enrollCourseId = request.GET.get("courseId")
	
	reqUrl=selected_mooc.secondaryUrl + "/user/" +request.user.username
	user = requests.get(reqUrl)
	user = user.json()
	#print user
	user['enrolled'].append(selected_mooc.groupName+":" + enrollCourseId)
	
	print "enrollCourseId", enrollCourseId
	return


def addCourse(request):
	#Takes place in the context of a logged in user
	#1 He is a registered User-not needed since user already logged in
	#2 He cannot add a course already added(unique course_id)
	#3 He(may or may not choose the category before adding a course?) adds a course and fills in a category(some fields are mandatory)
	#4 
	global selected_mooc, headers
	course={}
	print "Here in add course"
	course['category']= "Cat"#request.POST.get('category')
	course["title"] = request.POST.get("title")
	course["dept"] = request.POST.get("dept")
	course["section"] = "1"
	course["term"] =  "Fall" #request.POST.get("term")
	course["instructor"] = request.user.first_name +" "+ request.user.last_name 
	course["days"] = request.POST.getlist('days')
	course["description"] = request.POST.get("desc")
	course["attachment"] = "No attachments"
	course["hours"] = request.POST.get('time')
	course["version"] = "0"
	course["year"] = "2013"
	
	#print 'course' , course
	
	reqUrl=selected_mooc.secondaryUrl+"/course"
    	#print reqUrl
    	#print headers
    	response=requests.post(reqUrl, json.dumps(course),headers=headers)
    	data=response.json()
   
    	courseId=data['id']
    	if response.status_code == 200:
        	reqUrl=selected_mooc.secondaryUrl + "/user/" +request.user.username
        	user = requests.get(reqUrl)
        	user = user.json()
        	#print user
        	user['own'].append(selected_mooc.groupName+":" + courseId)
        	reqUrl=selected_mooc.secondaryUrl + "/user/update/"+request.user.username
        	update_response=requests.put(reqUrl, json.dumps(user),headers=headers)
       
        	if update_response.status_code ==200:
            		print "Course added successfully"
	
	return render_to_response('successPage.html', {'message':"Course Successfully Added !!!"}, context_instance=RequestContext(request))
			
courseDict = {}
def listCourseToEnroll(request):
	
	global selected_mooc, headers,courseDict
	setMooc()
	print "Here in enroll course"
	
	reqUrl=selected_mooc.secondaryUrl + "/course/list"
	course = requests.get(reqUrl)
	course = course.json()
	
	#print course['list']
	course = course['list']
			

	for elem in course:
		courseDict[elem['id']] = elem['title']
	
	#for elem in courseDict:
		#print elem, courseDict[elem]
				
	#courseDict = {'key1':'val1', 'key2':'val2'}				
	return render_to_response('listCourseToEnroll.html', {'courseDict':courseDict} , context_instance=RequestContext(request))
	#mylist = ['item 1', 'item 2', 'item 3']
	#return render_to_response('listCourseToEnroll.html', {'mylistx':courseDict}, context_instance=RequestContext(request))
				
def removeCourse(request):
	#takes place in the context of a logged in user
	#1 Can only delete a course added by him th
	return

def dropCourse(request):
	return

	
	
	
