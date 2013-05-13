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

def home(request):
	return render_to_response('home.html', RequestContext(request, {}))

def home(request):
	return render_to_response('home.html', RequestContext(request, {}))

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
									
				return render_to_response('home.html',{},RequestContext(request))
			else:
				state = "Your account is not active, please contact the site admin."
		else:
			state = "Your username and/or password were incorrect."
  	
	return render_to_response('login.html',{'state':state, 'username': username},RequestContext(request, {}))

def createCourse(request):
	reqUrl=selected_mooc.primaryUrl + '/category/list'
	categories = requests.get(reqUrl)
	categories = categories.json()
	categories=categories['list']
	catoutput={}
	for category in categories:
		catoutput[category['name']] =category['name']
		print catoutput[category['name']]
				
	return render_to_response('createCourse.html',{'catoutput':catoutput}, RequestContext(request, {}))		
			
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
	
	reqUrl=selected_mooc.primaryUrl + "/user/" +request.user.username
	user = requests.get(reqUrl)
	user = user.json()
	#print user
	user['enrolled'].append(selected_mooc.groupName+":" + enrollCourseId)
	
	print "enrollCourseId", enrollCourseId
	reqUrl=selected_mooc.primaryUrl + "/user/update/"+request.user.username
	update_response=requests.put(reqUrl, json.dumps(user),headers=headers)

	if update_response.status_code ==200:
    		print "Course enrolled successfully"
    		
    	return render_to_response('successPage.html', {'message':"Course Successfully Enrolled !!!"}, context_instance=RequestContext(request))



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
	
	reqUrl=selected_mooc.primaryUrl+"/course"
    	#print reqUrl
    	#print headers
    	response=requests.post(reqUrl, json.dumps(course),headers=headers)
    	data=response.json()
   
    	courseId=data['id']
    	if response.status_code == 200:
        	reqUrl=selected_mooc.primaryUrl + "/user/" +request.user.username
        	user = requests.get(reqUrl)
        	user = user.json()
        	#print user
        	user['own'].append(selected_mooc.groupName+":" + courseId)
        	reqUrl=selected_mooc.primaryUrl + "/user/update/"+request.user.username
        	update_response=requests.put(reqUrl, json.dumps(user),headers=headers)
       
        	if update_response.status_code ==200:
            		print "Course added successfully"
	
	return render_to_response('successPage.html', {'message':"Course Successfully Added !!!"}, context_instance=RequestContext(request))
			

def listCourseToEnroll(request):
	
	global selected_mooc, headers
	courseDict = {}
	setMooc()
	print "Here in enroll course"
	
	reqUrl=selected_mooc.primaryUrl + "/course/list"
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


def listCourseToDrop(request):
		
	global selected_mooc, headers
	setMooc()
	print "Here in enroll course"
	courseDict = {}
	reqUrl=selected_mooc.primaryUrl + "/course/list"
	course = requests.get(reqUrl)
	course = course.json()
		
	#print course['list']
	course = course['list']
				
	reqUrl=selected_mooc.primaryUrl + "/user/" +request.user.username
	user = requests.get(reqUrl)
	user = user.json()
	userEnrolledList = user['enrolled']
	
	userEnrolledcourseids = []
	#print "USER ENROLLED LIST-------"
	for elem in userEnrolledList:
		#print elem
		userEnrolledcourseids.append(elem.split(":")[1])
	#print "-----------xxxxxx--------------"
	#for elem in userEnrolledcourseids:
		#print elem
	
	#print "-------------------------"
	
	#print "COURSE LIST-------"
	for elem in course:
		#print elem['id']
		if elem['id'] in userEnrolledcourseids:
			courseDict[elem['id']] = elem['title']
		
	#for elem in courseDict:
		#print elem, courseDict[elem]
					
	#courseDict = {'key1':'val1', 'key2':'val2'}				
	return render_to_response('listCourseToDrop.html', {'courseDict':courseDict} , context_instance=RequestContext(request))
	#mylist = ['item 1', 'item 2', 'item 3']
	#return render_to_response('listCourseToDrop.html', {'mylistx':courseDict}, context_instance=RequestContext(request))

def listCourseToDelete(request):
	
	global selected_mooc, headers
	setMooc()
	print "Here in delete course"
	courseDict = {}
	reqUrl=selected_mooc.primaryUrl + "/course/list"
	course = requests.get(reqUrl)
	course = course.json()
		
	#print course['list']
	course = course['list']
				
	reqUrl=selected_mooc.primaryUrl + "/user/" +request.user.username
	user = requests.get(reqUrl)
	user = user.json()
	userOwnList = user['own']
					
	userOwnCourseids = []
	
	for elem in userOwnList:
		#print elem
		userOwnCourseids.append(elem.split(":")[1])
	
	for elem in course:
		print elem['id']
		if elem['id'] in userOwnCourseids:
			courseDict[elem['id']] = elem['title']
		
	#for elem in courseDict:
		#print elem, courseDict[elem]
					
	#courseDict = {'key1':'val1', 'key2':'val2'}				
	return render_to_response('listCourseToDelete.html', {'courseDict':courseDict} , context_instance=RequestContext(request))
	#mylist = ['item 1', 'item 2', 'item 3']
	#return render_to_response('listCourseToDelete.html', {'mylistx':courseDict}, context_instance=RequestContext(request))

def deleteCourse(request):
	#takes place in the context of a logged in user
	#1 Can only delete a course added by him th
	print "Here in delete course"
	
	deleteCourseId = request.GET.get("courseId")
	reqUrl = selected_mooc.primaryUrl + "/course/" + deleteCourseId
	
	#print reqUrl
	response = requests.delete(reqUrl)
	if response.status_code == 200:
		print "Course deleted successfully"
        reqUrl=selected_mooc.primaryUrl + "/user/" +request.user.username
    	user = requests.get(reqUrl)
    	user = user.json()
    	print user
    	user['own'].remove(selected_mooc.groupName+":" + deleteCourseId)
    	
    	print "deleteCourseId", deleteCourseId
    	reqUrl=selected_mooc.primaryUrl + "/user/update/"+request.user.username
    	update_response=requests.put(reqUrl, json.dumps(user),headers=headers)

    	if update_response.status_code ==200:
        	print "Course dropped successfully"
           	return render_to_response('successPage.html', {'message':"Course Successfully Deleted !!!"},context_instance=RequestContext(request))

        return render_to_response('successPage.html', {'message':"Course could not be Deleted. Please try again !!!"}, context_instance=RequestContext(request))

 

def dropCourse(request):
	#takes place in the context of a logged in user
	# for enrolling we need to confirm 
	#1. He is registered User(username in sqlite) -- not required 
	#2 	He can register in the course added by him
	#3 	He must not be already enrolled
	#4  Enrolling means his data in mongo is updated
	global selected_mooc, headers
	
	print "here in drop course"
	dropCourseId = request.GET.get("courseId")
	
	reqUrl=selected_mooc.primaryUrl + "/user/" +request.user.username
	user = requests.get(reqUrl)
	user = user.json()
	#print user
	user['enrolled'].remove(selected_mooc.groupName+":" + dropCourseId)
	
	print "dropCourseId", dropCourseId
	reqUrl=selected_mooc.primaryUrl + "/user/update/"+request.user.username
	update_response=requests.put(reqUrl, json.dumps(user),headers=headers)

	if update_response.status_code ==200:
    		print "Course dropped successfully"
    		return render_to_response('successPage.html', {'message':"Course Successfully Dropped !!!"}, context_instance=RequestContext(request))

    	return render_to_response('successPage.html', {'message':"Course could not be Dropped. Please try again !!!"}, context_instance=RequestContext(request))


def getCategories(request):
	reqUrl=selected_mooc.primaryUrl + '/category/list'
	category = requests.get(reqUrl)
	category = category.json()
	
	return category
	
def addCategory(request):
	return render_to_response('addCategory.html', RequestContext(request, {}))
			
def addCategoryInDb(request):
	print "In addCategoryInDb"
	return