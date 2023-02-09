from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("category", views.category, name="category"),
    path("<int:listing_id>", views.listing_page, name="listing_page"),
    path("<int:listing_id>/add", views.add, name="add"),
    path("<int:listing_id>/delete", views.delete, name="delete"),
    path("<int:listing_id>/close", views.close, name="close"),
    path("<int:listing_id>/edit", views.edit, name="edit"),
    path("category/<int:category_id>", views.listings_by_categories, name="listings_by_categories")
    
]

