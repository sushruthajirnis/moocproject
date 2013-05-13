from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'moocproject.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),
<<<<<<< HEAD
    url(r'^$','mooc.views.loginUser'),
    url(r'^login/$', 'mooc.views.loginUser'),
    url(r'^register/$', 'mooc.views.addUser'),
    url(r'^signout/$','mooc.views.userLogout'),
    url(r'^addCourse/$','mooc.views.addCourse'),
    url(r'^courses/$','mooc.views.createCourse'),
    url(r'^createCourse/$','mooc.views.createCourse'),
    url(r'^home/$','mooc.views.home'),
    url(r'^listCourseToEnroll/$','mooc.views.listCourseToEnroll',name="listC"),
    url(r'^listCourseToDrop/$','mooc.views.listCourseToDrop',name="dropC"),
    url(r'^enrollCourse/$','mooc.views.enrollCourse',name="enroll"),
    url(r'^dropCourse/$','mooc.views.dropCourse',name="drop"),
    url(r'^listCourseToDelete/$','mooc.views.listCourseToDelete',name="delete"),
    url(r'^deleteCourse/$','mooc.views.deleteCourse',name="deleteC"),
=======
    url(r'^$','mooc.views.login_user'),
    url(r'^login/$', 'mooc.views.login_user'),
    url(r'^register/$', 'mooc.views.add_user'),
    url(r'^signout/$','mooc.views.user_logout')
    
>>>>>>> c55e203933d2dace129e1700b9f45fc290de1e05
)

