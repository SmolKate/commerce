from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.db.models import Max, Count
from django.contrib.auth.decorators import login_required



from .models import User, Listing, Bid, ListingForm, Category, BidForm, Comment, CommentForm, Watchlist



def index(request):
    
    listings = Listing.objects.all()
    bids = Bid.objects.all()
    f=bids.values('listing').annotate(Max('user_bid'))
    
    
    return render(request, "auctions/index.html", {
        "listings":listings,         
        "maxvals": f,
        
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def new_listing(request):
    #    if request.method == "POST":
#        title = request.POST["title"]
#        description = request.POST["description"]
#        start_bid = request.POST["start_bid"]
#        username = request.user
#        try:
#            listing = Listing.objects.create()
            
#        except IntegrityError:
#            return render(request, "auctions/listingform.html", {
#                "message": "Listing already exist."
#            })
        
#        return HttpResponseRedirect(reverse("index"))
#    else:
#        return render(request, "auctions/listingform.html")
        
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.username = request.user
            post.create_time = timezone.now()
            post.save()
            
        else:
            return render(request, "auctions/listingform.html", {
                    "form": form
                    })       
    else:
        form = ListingForm()
        return render(request, "auctions/listingform.html", {'form': form})
    
    return HttpResponseRedirect(reverse("index"))
            
def listing_page(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    form = BidForm()
    form2 = CommentForm()
    f=Bid.objects.filter(listing=listing_id).values('listing').annotate(Max('user_bid'))
    fd=Bid.objects.filter(listing=listing_id).aggregate(Max('user_bid'))['user_bid__max']
    name = Bid.objects.filter(listing=listing_id, user_bid=fd).first()

    comments = Comment.objects.filter(listing=listing_id).all()

    username = request.user
    if username.is_authenticated:
        watchlists = Watchlist.objects.filter(username=username, listing=listing_id)
    else:
        watchlists = []

    if request.method == "POST":        
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.username = request.user
            bid.bid_time = timezone.now()
            bid.listing = listing
            userbid=request.POST["user_bid"]
            if bid.user_bid >= listing.start_bid:
                if name is None or bid.user_bid > name.user_bid:
                    bid.save()
                else:
                    return render(request, "auctions/listing_page.html", {
                        "message": "Your bid should be more than the current price.",
                        "listing":listing,
                        "name": name,
                        "form": form,
                        "form2": form2,
                        "comments": comments,
                        "watchlists": watchlists, 
                        }) 
            else:
                return render(request, "auctions/listing_page.html", {
                    "message": "Your bid should be at least as large as the current price.",
                    "listing":listing,
                    "name": name,
                    "form": form,
                    "form2": form2,
                    "comments": comments,
                    "watchlists": watchlists, 
                    })  

        form2 = CommentForm(request.POST)   
        if form2.is_valid():
            com = form2.save(commit=False)
            com.username = request.user
            com.comment_time = timezone.now()
            com.listing = listing
            com.save()
            
    else:
        return render(request, "auctions/listing_page.html", {
            "listing":listing,
            "name": name,
            "form": form,
            "form2": form2,
            "comments": comments,
            "watchlists": watchlists, 
            })
    return HttpResponseRedirect(reverse("listing_page", args=(listing.id,)))

@login_required
def watchlist (request):
    listings = Listing.objects.all()
    username = request.user
    watchlists = Watchlist.objects.filter(username=username)
    bids = Bid.objects.all()
    f=bids.values('listing').annotate(Max('user_bid'))
    

    return render(request, "auctions/watchlist.html", {
        "watchlists": watchlists,
        "listings": listings, 
        "maxvals": f,         
    })

@login_required    
def add (request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    username = request.user
    watch_add = Watchlist (listing=listing, username=username)
    watch_add.save()
    return HttpResponseRedirect(reverse("listing_page", args=(listing.id,)))

@login_required
def delete (request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    username = request.user
    watch_del = Watchlist.objects.get(listing=listing, username=username)
    watch_del.delete()
    return HttpResponseRedirect(reverse("listing_page", args=(listing.id,)))

@login_required
def close (request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    username = request.user
    listing.status = "close"
    listing.save()
    return HttpResponseRedirect(reverse("index"))

@login_required
def edit (request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    form = ListingForm(instance=listing)
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            post = form.save(commit=False)
            post.username = request.user
            post.create_time = timezone.now()
            post.save()
            
        else:
            return render(request, "auctions/listingform.html", {
                    "form": form
                    })       
    else:
        return render(request, "auctions/listingform.html", {'form': form})
      
    return HttpResponseRedirect(reverse("listing_page", args=(listing.id,)))

def category (request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
                    "categories": categories
                    })

def listings_by_categories (request, category_id):
    category = Category.objects.get(pk = category_id)
    listings = category.cat_listings.all()
    bids = Bid.objects.all()
    f=bids.values('listing').annotate(Max('user_bid'))
    
    return render(request, "auctions/listings_by_categories.html", {
        "listings":listings,         
        "maxvals": f,
        "category": category
        
    })

