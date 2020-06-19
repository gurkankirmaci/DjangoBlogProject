from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms  import PasswordChangeForm


# Create your views here.
from product.models import Category
from home.models import UserProfile
from user.forms import UserUpdateForm,ProfileUpdateForm

from product.models import Comment,Product,Images
from content.models import Menu
from content.models import Content
from content.models import ContentForm
from product.models import ProductImageForm
from django.contrib.auth.models import User



def index(request):
    category = Category.objects.all()
    menu = Menu.objects.all()
    current_user = request.user  # Access User Session information

    profile = UserProfile.objects.get(user_id =current_user.id)
    #return HttpResponse(profile)
    context = {'category': category,
               'profile': profile ,
               'menu': menu,
               }
    return render(request,'user_profile.html',context)

def user_update(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST,instance =request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance = request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('/user')

    else:
        category = Category.objects.all()
        menu = Menu.objects.all()
        user_form = UserUpdateForm(instance =request.user)
        profile_form = ProfileUpdateForm(instance =request.user.userprofile)
        context = {
            'category':category,
            'user_form':user_form,
            'profile_form':profile_form,
            'menu': menu,
        }
        return render(request,'user_update.html',context)

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request,user) #important
            messages.success(request,'Your password was succesfully update !')
            return HttpResponseRedirect('/user')
        else:
            messages.error(request,'Please correct the error below.<br>'+ str(form.errors))
            return HttpResponseRedirect('/user/password')
    else:
        category = Category.objects.all()
        menu = Menu.objects.all()
        form = PasswordChangeForm(request.user)
        return render(request,'change_password.html',
                 { 'form':form,
                   'category' :category,
                   'menu': menu,
        })

@login_required(login_url='/login') #check login
def comments(request):
    category = Category.objects.all()
    menu = Menu.objects.all()
    current_user = request.user
    comments = Comment.objects.filter(user_id=current_user.id)
    context = {
        'category': category,
        'comments': comments,
        'menu': menu,
    }
    return render(request, 'user_comments.html',context)

@login_required(login_url='/login') #check login
def deletecomment(request,id):
    current_user = request.user
    Comment.objects.filter(id = id,user_id=current_user.id).delete()
    messages.success(request ,'Comment deleted..')
    return HttpResponseRedirect('/user/comments')

@login_required(login_url='/login') #check login
def contents(request):
    category = Category.objects.all()
    menu = Menu.objects.all()
    current_user = request.user
    contents = Product.objects.filter(user_id=current_user.id).order_by('-id')
    context = {
        'category': category,
        'menu'    : menu,
        'contents':  contents,
    }
    return render(request, 'user_contents.html', context)

@login_required(login_url='/login') #check login
def addcontent(request):
    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES )
        if form.is_valid():
            current_user = request.user
            data = Product() #model ile bağlantı kur
            data.user_id = current_user.id
            data.title = form.cleaned_data['title']
            data.keywords = form.cleaned_data['keywords']
            data.description = form.cleaned_data['description']
            data.image = form.cleaned_data['image']
            data.category = form.cleaned_data['category']
            data.amount = form.cleaned_data['amount']
            data.slug = form.cleaned_data['slug']
            data.detail = form.cleaned_data['detail']
            data.status = 'False'
            data.save() #veritabanına kaydet
            messages.success(request,'Your Content Insterted Successfuly ')
            return HttpResponseRedirect('/user/contents')
        else:
            messages.success(request,'Content Form Error :'  +str(form.errors))
            return HttpResponseRedirect('/user/addcontent')

    else:
        category = Category.objects.all()
        menu = Menu.objects.all()
        form = ContentForm()
        context = {
            'menu': menu,
            'category': category,
            'form': form,
         }
        return render(request, 'user_addcontent.html',context)


@login_required(login_url='/login') #check login
def contentedit(request,id):
    content = Product.objects.get(id=id) #category geliyor
    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES, instance =content)
        if form.is_valid():
            form.save()
            messages.success(request,'Your Content Updated Successfuly')
            return HttpResponseRedirect('/user/')
        else:
            messages.success(request, 'Content Form Error :' + str(form.errors))
            return HttpResponseRedirect('/user/contentedit/' +str(id))
    else:
        category = Category.objects.all()
        menu = Menu.objects.all()
        form = ContentForm(instance=content)
        context = {
            'category': category,
            'form': form,
            'menu': menu,
        }
        return render(request,'user_addcontent.html',context)


@login_required(login_url='/login') #check login
def contentdelete(request,id):
    current_user = request.user
    Product.objects.filter(id=id, user_id = current_user.id).delete() #product silme
    messages.success(request, 'Product deleted..')
    return HttpResponseRedirect('/user/')


def contentaddimage(request,id):
    if request.method == 'POST':
        lasturl = request.META.get('HTTP_REFERER')
        form = ProductImageForm(request.POST,request.FILES)
        if form.is_valid():
            data = Images()
            data.title = form.cleaned_data['title']
            data.product_id = id
            data.image = form.cleaned_data['image']
            data.save()
            messages.success(request,'Your image has been successfully uploaded...')
            return HttpResponseRedirect(lasturl)
        else:
            messages.warning(request,'Form Error:' +str(form.errors))
            return HttpResponseRedirect(lasturl)
    else:
        product = Product.objects.get(id=id)
        images = Images.objects.filter(product_id=id)
        form = ProductImageForm()
        context = {
            'product':product,
            'images':images,
            'form':form,
        }
        return render(request,'content_gallery.html',context)


@login_required(login_url='/login') #check login
def deleteimage(request,id):
    lasturl = request.META.get('HTTP_REFERER')
    Images.objects.filter(id=id).delete()
    messages.warning(request,'Your image is deleted successfully!')
    return HttpResponseRedirect(lasturl)
