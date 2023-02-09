from django.contrib import admin
from .models import User, Listing, Bid, Comment, Category, Watchlist

# Register your models here.
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "start_bid", "status", "create_time", "modify_time")
	#readonly_fields = ("create_time", "modify_time")

admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Watchlist)
