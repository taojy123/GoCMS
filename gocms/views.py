# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from models import *
import os
import uuid

def index(request):
    return HttpResponseRedirect("/customers")


@login_required(login_url="/loginpage")
def added(request):
    captions = Caption.objects.all()
    return render_to_response('added.html', locals())


@login_required(login_url="/loginpage")
def customers(request):
    rs = Customer.objects.filter(user=request.user).order_by("-id")

    info_ids = rs.values_list("info__id", flat=True)
    infos = Info.objects.filter(id__in=info_ids)
    caption_ids = infos.values_list("caption__id", flat=True)
    captions = Caption.objects.filter(id__in=caption_ids)
    for customer in rs:
        customer.contents = []
        for caption in captions:
            content = customer.get_content(caption.name)
            customer.contents.append(content)


    return render_to_response('customers.html', locals())


@login_required(login_url="/loginpage")
def customer_add(request):
    name = request.REQUEST.get('name')
    phone = request.REQUEST.get('phone')
    company = request.REQUEST.get('company')
    remark = request.REQUEST.get('remark')
    caption_id = request.REQUEST.get('caption_id')
    caption_name = request.REQUEST.get('caption_name')
    content = request.REQUEST.get('content')

    if not name:
        return HttpResponse("<script>alert('请填写客户姓名'); top.location.href='/added'</script>")

    if caption_id:
        caption = Caption.objects.get(id=caption_id)
    elif caption_name:
        rs = Caption.objects.filter(name=caption_name)
        if rs:
            caption = rs[0]
        else:
            caption = Caption()
            caption.name = caption_name
            caption.save()
    else:
        caption = None

    if caption and content:
        info = Info()
        info.caption = caption
        info.content = content
        info.save()
    else:
        info = None

    customer = Customer()
    customer.user = request.user
    customer.name = name
    customer.phone = phone
    customer.company = company
    customer.remark = remark
    customer.save()

    if info:
        customer.info.add(info)
        customer.save()

    return HttpResponseRedirect("/customers")


@login_required(login_url="/loginpage")
def customer_del(request):
    id = request.REQUEST.get("id")
    Customer.objects.filter(id=id).delete()
    return HttpResponseRedirect("/customers")


@login_required(login_url="/loginpage")
def customer_update(request):
    id = request.REQUEST.get("id")
    name = request.REQUEST.get('name')
    phone = request.REQUEST.get('phone')
    company = request.REQUEST.get('company')
    remark = request.REQUEST.get('remark')

    customer = Customer.objects.get(id=id)
    customer.name = name
    customer.phone = phone
    customer.company = company
    customer.remark = remark
    customer.save()

    return HttpResponseRedirect("/customers")


@login_required(login_url="/loginpage")
def customer_infos(request):
    id = request.REQUEST.get("id")
    customer = Customer.objects.get(id=id)
    captions = Caption.objects.all().order_by("-id")
    return render_to_response("customer_infos.html", locals())


@login_required(login_url="/loginpage")
def info_add(request):
    cid = request.REQUEST.get("cid")
    caption_id = request.REQUEST.get('caption_id')
    caption_name = request.REQUEST.get('caption_name')
    content = request.REQUEST.get('content')

    if caption_id:
        caption = Caption.objects.get(id=caption_id)
    elif caption_name:
        rs = Caption.objects.filter(name=caption_name)
        if rs:
            caption = rs[0]
        else:
            caption = Caption()
            caption.name = caption_name
            caption.save()
    else:
        caption = None

    if caption and content:
        rs = Info.objects.filter(caption=caption)
        if rs:
            info = rs[0]
        else:
            info = Info()
            info.caption = caption
        info.content = content
        info.save()
    else:
        info = None

    if info:
        customer = Customer.objects.get(id=cid)
        customer.info.add(info)
        customer.save()

    return HttpResponseRedirect("/customer_infos/?id=" + cid)


@login_required(login_url="/loginpage")
def info_del(request):
    id = request.REQUEST.get("id")
    cid = request.REQUEST.get("cid")
    Info.objects.filter(id=id).delete()
    return HttpResponseRedirect("/customer_infos/?id=" + cid)


@login_required(login_url="/loginpage")
def info_update(request):
    id = request.REQUEST.get("id")
    cid = request.REQUEST.get("cid")
    content = request.REQUEST.get('content')

    info = Info.objects.get(id=id)
    info.content = content
    info.save()

    return HttpResponseRedirect("/customer_infos/?id=" + cid)


#==================== auth ===========================================

def loginpage(request):
    return render_to_response('loginpage.html', locals())

def registerpage(request):
    return render_to_response('registerpage.html', locals())

def login(request):
    username = request.REQUEST.get('username', '')
    password = request.REQUEST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
    return HttpResponseRedirect("/")

def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return HttpResponseRedirect("/")

def register(request):
    msg = ""
    username = request.REQUEST.get('username')
    password1 = request.REQUEST.get('password1')
    password2 = request.REQUEST.get('password2')
    if username and password1 and password2:
        if User.objects.filter(username=username):
            msg = "该用户名已被注册"
            return render_to_response('registerpage.html', locals())
        if password1 == password2:
            user = User()
            user.username = username
            user.set_password(password1)
            user.save()
            return HttpResponseRedirect("/")
    msg = "输入有误，请重新输入"
    return render_to_response('registerpage.html', locals())

#======================================================================
