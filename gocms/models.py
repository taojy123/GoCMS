# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
import datetime
import time


class Caption(models.Model):
    name = models.CharField(max_length=255, blank=True , null=True)


class Info(models.Model):
    caption = models.ForeignKey(Caption)
    content = models.CharField(max_length=2048, blank=True , null=True)


class Customer(models.Model):
    user = models.ForeignKey(User, blank=True ,null=True)
    name = models.CharField(max_length=255, blank=True , null=True)
    phone = models.CharField(max_length=255, blank=True , null=True)
    company = models.CharField(max_length=255, blank=True , null=True)
    remark = models.CharField(max_length=255, blank=True , null=True)
    info = models.ManyToManyField(Info)

    @property
    def show_info(self):
    	s = ""
    	infos = self.info.all()
    	for info in infos:
    		s += "%s:%s; " % (info.caption.name, info.content)
    	return s

    def get_content(self, caption_name):
        try:
            caption = Caption.objects.get(name=caption_name)
            return self.info.get(caption=caption).content
        except:
            return ""