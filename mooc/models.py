from django.db import models

# Create your models here.

class Mooc(models.Model):
	groupName = models.CharField(max_length=256)
	primaryUrl = models.CharField(max_length=256)
	secondaryUrl = models.CharField(max_length=256)
	default = models.BooleanField(default=False)
	
	def __unicode__(self):
		return u'%s, %s, %s' % (self.groupName, self.primaryUrl , self.secondaryUrl)