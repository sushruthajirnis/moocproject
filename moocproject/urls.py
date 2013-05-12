from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'moocproject.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$','mooc.views.login_user'),
    url(r'^login/$', 'mooc.views.login_user'),
    url(r'^register/$', 'mooc.views.add_user'),
    url(r'^signout/$','mooc.views.user_logout')
    
)

