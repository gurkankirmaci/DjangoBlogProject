from unicodedata import category

from django.contrib.auth import logout, authenticate, login
from django.http import  HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
import json


# Create your views here.
from home.models import Setting, ContactFormu, ContactFormMessage, UserProfile

from product.models import Product,Category

from product.models import Images,Comment

from home.forms import SearchForm

from home.forms import SignUpForm
from content.models import Menu,Content,CImages

from home.models import FAQ


def index(request):
    current_user =request.user
    setting = Setting.objects.get(pk=1)
    sliderdata= Product.objects.all()[:4]
    category= Category.objects.all()
    menu = Menu.objects.all()
    dayproducts = Product.objects.all()[:3]
    lastproducts = Product.objects.all().order_by('-id')[:2]
    randomproducts=Product.objects.all().order_by('?')[:2]
    product = Content.objects.filter(type='product', status=True)
    news= Content.objects.filter(type='haber',status =True).order_by('-id')[:5]
    announcements = Content.objects.filter(type='duyuru',status =True).order_by('-id')[:5]


    context = {'setting': setting,
               'category': category,
               'menu': menu,
               'page': 'home',
               'news': news,
               'announcements': announcements,
               'sliderdata': sliderdata,
               'dayproducts': dayproducts,
               'lastproducts': lastproducts,
               'randomproducts': randomproducts,
               }
    return render(request, 'index.html', context)

def hakkimizda(request):
    menu = Menu.objects.all()
    setting = Setting.objects.get(pk=1)
    context = {'setting': setting,
               'page': 'hakkimizda',
               'category': category,
               'menu': menu,
               }
    return render(request, 'hakkimizda.html', context)

def referanslar(request):
    menu = Menu.objects.all()
    setting = Setting.objects.get(pk=1)
    context = {'setting': setting,
               'page': 'referanslar',
               'category': category,
               'menu': menu, }
    return render(request, 'referanslar.html', context)


def iletisim(request):

    if request.method == 'POST':           #bu bölüm formu kaydetmek için
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

    setting= Setting.objects.get(pk=1)       #bu kısım forma ulaşmak için
    menu = Menu.objects.all()
    form= ContactFormu()
    context={'setting':setting,
             'form':form,
             'category': category,
             'menu': menu,
             }
    return render(request,'iletisim.html',context)

def category_products(request,id,slug):
    category = Category.objects.all()
    menu = Menu.objects.all()
    categorydata = Category.objects.get(pk=id)
    products = Product.objects.filter(category_id=id)
    context = {
               'products' : products,
               'category': category,
               'categorydata': categorydata,
               'menu': menu
               }
    return render(request,'products.html',context)

def product_detail(request,id,slug):
    category = Category.objects.all()
    try:
        product = Product.objects.get(pk=id)
        images  = Images.objects.filter(product_id=id)
        menu = Menu.objects.all()
        comments = Comment.objects.filter(product_id=id,status='True') #yorumları sayfada gösterme
        context = {'product': product,
                   'category':category,
                   'images': images,
                   'comments': comments,
                   'menu': menu,
                   }
        return render(request,'product_detail.html',context)
    except:
        messages.warning(request, "Hata ! İlgili içerik bulunamadı ")
        link = '/error'
        return HttpResponseRedirect(link)

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
            menu = Menu.objects.all()
            query = form.cleaned_data['query']  #formdan bilgiyi al
            catid = form.cleaned_data['catid']  #get form data

            if catid == 0:
                     products = Product.objects.filter(title__icontains= query)  #select * from product where title like %query%
            else:
                     products = Product.objects.filter(title__icontains=query,category_id = catid)

            #return HttpResponse(products)
            context = {'products': products,
                       'category': category,
                       'menu': menu,
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
    menu = Menu.objects.all()
    context = {'category': category,
               'menu': menu,
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
            #Create data in profile table for user
            current_user = request.user
            data = UserProfile()
            data.user_id=current_user.id
            data.image = "images/users/default.png"
            data.save()
            messages.success(request,"Hoş Geldiniz...Üyelik İşleminiz Başarılı,Lütfen Giriş Yapınız...")
            return HttpResponseRedirect('/login')

    form = SignUpForm()
    category = Category.objects.all()
    menu = Menu.objects.all()
    context = {'category': category,
               'form': form,
               'menu' : menu,
               }
    return render(request, 'signup.html', context)

def menu(request,id):
    try:
        content = Content.objects.get(menu_id = id)
        link='/content/'+str(content.id)+'/menu'
        return HttpResponseRedirect(link)
    except:
        messages.warning(request, "Hata ! İlgili içerik bulunamadı ")
        link = '/error'
        return HttpResponseRedirect(link)


def contentdetail(request,id,slug):
    category = Category.objects.all()
    menu = Menu.objects.all()

    try:
        content = Content.objects.get(pk=id)
        images = CImages.objects.filter(content_id=id)
        # return HttpResponse(link)
        context = {'content': content,
                   'category': category,
                   'menu': menu,
                   'images': images,
               }
        return render(request,'content_detail.html',context)
    except:
        messages.warning(request, "Hata ! İlgili içerik bulunamadı ")
        link = '/error'
        return HttpResponseRedirect(link)

def error(request):
    category = Category.objects.all()
    menu = Menu.objects.all()

    context = {
               'category': category,
               'menu': menu,
              }
    return render(request,'error_page.html',context)


def faq(request):
    menu = Menu.objects.all()
    category = Category.objects.all()
    faq = FAQ.objects.all().order_by('ordernumber')
    context = {
        'category': category,
        'menu': menu,
        'faq' : faq,
    }
    return render(request, 'faq.html', context)