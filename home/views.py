from unicodedata import category

from django.contrib.auth import logout, authenticate, login
from django.http import  HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
import json


# Create your views here.
from home.models import Setting, ContactFormu, ContactFormMessage

from product.models import Product,Category

from product.models import Images,Comment

from home.forms import SearchForm

from home.forms import SignUpForm


def index(request):
    setting = Setting.objects.get(pk=1)
    sliderdata= Product.objects.all()[:4]
    category= Category.objects.all()
    dayproducts = Product.objects.all()[:3]
    lastproducts = Product.objects.all().order_by('-id')[:2]
    randomproducts=Product.objects.all().order_by('?')[:2]
    context = {'setting': setting,
               'category': category,
               'page': 'home',
               'sliderdata':sliderdata,
               'dayproducts': dayproducts,
               'lastproducts': lastproducts,
               'randomproducts': randomproducts,
               }
    return render(request, 'index.html', context)

def hakkimizda(request):
    setting = Setting.objects.get(pk=1)
    context = {'setting': setting,'page': 'hakkimizda','category': category, }
    return render(request, 'hakkimizda.html', context)

def referanslar(request):
    setting = Setting.objects.get(pk=1)
    context = {'setting': setting,'page': 'referanslar','category': category, }
    return render(request, 'referanslar.html', context)


def iletisim(request):

    if request.method == 'POST':
        form = ContactFormu(request.POST)
        if form.is_valid():
            data=ContactFormMessage() #model ile baglanti kur
            data.name =form.cleaned_data['name'] #formdan bilgi al
            data.email =form.cleaned_data['email']
            data.subject =form.cleaned_data['subject']
            data.message = form.cleaned_data['message']
            data.ip = request.META.get('REMOTE_ADDR')
            data.save() #veritabanına kaydet
            messages.success(request, "Mesajınız başarı ile gönderilmiştir,Teşekkür ederiz")
            return HttpResponseRedirect ('/iletisim')

    setting= Setting.objects.get(pk=1)
    form= ContactFormu()
    context={'setting':setting,'form':form,'category': category}
    return render(request,'iletisim.html',context)

def category_products(request,id,slug):
    category = Category.objects.all()
    categorydata = Category.objects.get(pk=id)
    products = Product.objects.filter(category_id=id)
    context = {'products' : products,
               'category': category,
               'categorydata': categorydata}
    return render(request,'products.html',context)

def product_detail(request,id,slug):
    category = Category.objects.all()
    product = Product.objects.get(pk=id)
    images  = Images.objects.filter(product_id=id)
    comments = Comment.objects.filter(product_id=id,status='True') #yorumları sayfada gösterme
    context = {'product': product,
               'category':category,
               'images': images,
               'comments': comments,
               }
    return render(request,'product_detail.html',context)

def content_detail(request,id,slug):
    category = Category.objects.all()
    product = Product.objects.filter(category_id=id)
    link ='/product/'+str(product[0].id)+'/'+product[0].slug
    #return HttpResponse(link)
    return HttpResponseRedirect (link)


def product_search(request):
    if request.method == 'POST': #form post edildiyse
        form = SearchForm(request.POST)
        if form.is_valid():
            category = Category.objects.all()

            query = form.cleaned_data['query']  #formdan bilgiyi al
            catid = form.cleaned_data['catid']  #get form data

            if catid == 0:
                     products = Product.objects.filter(title__icontains= query)  #select * from product where title like %query%
            else:
                     products = Product.objects.filter(title__icontains=query,category_id = catid)

            #return HttpResponse(products)
            context = {'products': products,
                       'category': category,
                        }
            return render(request, 'products_search.html',context)
    return HttpResponseRedirect('/')

def product_search_auto(request):
    if request.is_ajax():
        q = request.GET.get('term','')
        product = Product.objects.filter(title__icontains= q)
        results=[]
        for rs in product:
            product_json = {}
            product_json = rs.title
            results.append(product_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data,mimetype)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return HttpResponseRedirect('/')
        else:
            # Return an 'invalid login' error message.
            messages.warning(request, "Login Hatası ! Kullanıcı Adı veya Şifreniz Hatalı")
            return HttpResponseRedirect('/login')
    category = Category.objects.all()
    context = {'category': category,
               }
    return render(request, 'login.html', context)

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username,password=password)
            login(request,user)
            return HttpResponseRedirect('/')

    form = SignUpForm()
    category = Category.objects.all()
    context = {'category': category,
               'form': form,
                   }
    return render(request, 'signup.html', context)