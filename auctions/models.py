from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms
from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS


class User(AbstractUser):
    username = models.CharField(max_length=64, unique=True)
    password = models.CharField(max_length=64)
    email = models.EmailField(max_length=64, blank=True)

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

class Category(models.Model):
    category = models.CharField(max_length=64)
    
    def __str__(self):
        return self.category

class Listing(models.Model):
    title = models.CharField(max_length=64, unique=True, error_messages={'unique':"This listing is already exist."})
    image = models.ImageField(upload_to='images/%Y-%m-%d/', default= 'images/default.jpg', null=True, blank=True)
    description = models.TextField(max_length=200)
    start_bid = models.IntegerField(null=True)
    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name="us_listings")
    category = models.ForeignKey(Category, on_delete = models.SET_NULL, null=True, related_name="cat_listings")
    status = models.CharField(max_length=64, default='active')
    create_time = models.DateTimeField(auto_now_add=True)
    modify_time = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.title

class Bid(models.Model):
    user_bid = models.IntegerField(null=True)
    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name="us_bids")
    listing = models.ForeignKey(Listing, on_delete = models.CASCADE, related_name="list_bid")
    bid_time = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} made {self.user_bid} dollar(s) bid."

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete = models.CASCADE, related_name="list_comments")
    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name="us_comments")
    comment_text = models.TextField(max_length=200)
    comment_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment from {self.username}, date/time:{self.comment_time}."

class Watchlist(models.Model):
    listing = models.ForeignKey(Listing, on_delete = models.CASCADE, related_name="list_watchlist")
    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name="us_watchlist")

    class Meta:
        unique_together = ['listing', 'username']   
    def __str__(self):
        return f"{self.listing} is in the watchlist of {self.username}."



#class ListingForm(forms.Form):
#    title=forms.CharField(max_length=64)
#    start_bid=forms.IntegerField()
#    description=forms.CharField(max_length=200)
    


class ListingForm(forms.ModelForm):
    
    class Meta:
        model = Listing
        fields = ['title', 'image', 'description', 'category', 'start_bid']
        labels = {
            'start_bid': 'Start bid ($)',
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique': "This listing is already exist.",
            }
        }

    
        widgets = {
            'title': forms.TextInput (attrs={'class': 'form-control', 'id': 'fields'}),
            'image': forms.FileInput (attrs={'class': 'form-control', 'id': 'fields'}),
            'description': forms.Textarea (attrs={'class': 'form-control', 'rows': 5, 'id': 'fields'}),
            'category': forms.Select (attrs={'class': 'form-control', 'id': 'fields'}),
            'start_bid': forms.NumberInput (attrs={'class': 'form-control','id': 'fields'})
        }
    
class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['user_bid']
        labels = {
            'user_bid': 'Your bid ($)',
        }
        widgets = {
            'user_bid': forms.NumberInput (attrs={'class': 'form-control','id': 'fields'})
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_text']
        labels = {
            'comment_text': 'Your comment',
        }
        widgets = {
            'comment_text': forms.Textarea (attrs={'class': 'form-control','id': 'fields', 'rows': 4})
        }