from ckeditor.widgets import CKEditorWidget
from django.db import models
from lib2to3.fixes.fix_idioms import TYPE
# Create your models here.
from django.forms import ModelForm, TextInput, Select, FileInput, NumberInput
from django.urls import reverse
from django.utils.safestring import mark_safe
from ckeditor_uploader.fields import RichTextUploadingField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from django.contrib.auth.models import User


class Category(MPTTModel):
    STATUS = (
        ('True', 'Evet'),
        ('False', 'Hayır')
    )

    title = models.CharField(max_length=150)
    keywords = models.CharField(blank=True,max_length=255)
    description = models.CharField(blank=True,max_length=255)
    image=models.ImageField(blank=True,upload_to='images/')
    status = models.CharField(max_length=10,choices=STATUS)
    slug=models.SlugField(null=False , unique=True)
    parent = TreeForeignKey('self',blank=True,null=True,related_name='children',on_delete=models.CASCADE)
    create_at =models.DateTimeField(auto_now_add=True)
    update_at =models.DateTimeField(auto_now=True)

    class MPTTMeta:
       order_insertion_by = ['title']

    def __str__(self):
       full_path = [self.title]
       k= self.parent
       while k is not None:
            full_path.append(k.title)
            k = k.parent
       return ' / '.join(full_path[::-1])

    def image_tag(self):
        return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
    image_tag.short_description = 'Image'

    def get_absolute_url(self):
        return reverse ('category_detail', kwargs= {'slug': self.slug} )



class Product(models.Model):


    STATUS = (
        ('True', 'Evet'),
        ('False', 'Hayır')
    )
    user = models.ForeignKey(User ,on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE) #relation with category table
    title = models.CharField(max_length=150)
    keywords = models.CharField(blank=True,max_length=255)
    description = models.CharField(blank=True,max_length=255)
    image=models.ImageField(blank=True,upload_to='images/')
    amount=models.IntegerField(default=1)
    detail=RichTextUploadingField()
    slug = models.SlugField(null=False , unique=True)
    status = models.CharField(max_length=10,choices=STATUS)
    create_at =models.DateTimeField(auto_now_add=True)
    update_at =models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def image_tag(self):
        return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
    image_tag.short_description = 'Image'

    def catimg_tag(self):
        return mark_safe((Category.status))

    def get_absolute_url(self):
        return reverse ('product_detail', kwargs= {'slug': self.slug} )

class Images(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=50,blank=True)
    image = models.ImageField(blank=True,upload_to='images/')
    def __str__(self):
        return self.title

    def image_tag(self):
        return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
    image_tag.short_description = 'Image'

class ProductImageForm(ModelForm):
    class Meta:
        model = Images
        fields = ['title','image']

class Comment(models.Model):
    STATUS = (
        ('New','Yeni'),
        ('True','Evet'),
        ('False','Hayır')
    )
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    subject= models.CharField(max_length=50)
    comment=models.TextField(max_length=200,blank=True)
    rate=models.IntegerField(blank=True)
    status=models.CharField(max_length=10,choices=STATUS,default='New')
    ip=models.CharField(blank=True,max_length=20)
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['subject','comment','rate' ]

class ContentForm(ModelForm):
    class Meta:
        model = Product
        fields = ['category','title','slug','keywords','description','image','detail','amount' ]
        widgets ={
            'title'    :TextInput(attrs={'class' : 'input','placeholder':'title' }),
            'slug'     :TextInput(attrs={'class' : 'input','placeholder':'slug' }),
            'keywords' :TextInput(attrs={'class' : 'input','placeholder':'keywords' }),
            'description':TextInput(attrs={'class' : 'input','placeholder':'description' }),
            'category': Select(attrs={'class': 'input', 'placeholder': 'city'}, choices=Category.objects.all()),
            'image'      : FileInput(attrs={'class' : 'input' , 'placeholder': 'image',}),
            'detail'    :CKEditorWidget(), #ckeditor input
            'amount': NumberInput(attrs={'class':'input', 'placeholder': 'number'})

        }