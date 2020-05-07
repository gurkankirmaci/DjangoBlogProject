from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
from product.models import CommentForm,Comment


def index(request):
    return HttpResponse("Product Page")

@login_required(login_url='/login')  #check login
def addcomment(request,id):
    url = request.META.get('HTTP_REFERER')  # GET LAST URL
    if request.method == 'POST': #FORM POST EDİLDİYSE
        form = CommentForm(request.POST)
        if form.is_valid():
            current_user=request.user  #Access User Session information

            data = Comment()  # model ile baglanti kur
            data.user_id = current_user.id
            data.product_id = id
            data.subject = form.cleaned_data['subject']
            data.comment = form.cleaned_data['comment']
            data.rate = form.cleaned_data['rate']
            data.ip = request.META.get('REMOTE_ADDR')  #CLIENT COMPUTER IP ADDRESS
            data.save() #veritabanına kaydet

            messages.success(request,"Yorumunuz basari ile kaydedilmistir,Tesekkur Ederiz")

            return HttpResponseRedirect(url)
            #return HttpResponse("Kaydedildi")
    messages.warning(request,"Yorumunuz kaydedilmedi lutfen tekrar deneyin")
    return HttpResponseRedirect(url)
