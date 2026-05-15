from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Location)
admin.site.register(Category)
admin.site.register(Company)
admin.site.register(Status)
admin.site.register(Currency)

admin.site.register(Tender)
admin.site.register(TenderAttachment)

admin.site.register(Bid)
admin.site.register(BidDocument)

admin.site.register(SavedTender)
admin.site.register(Evaluation)

admin.site.register(CategoryCompany)
admin.site.register(CategoryTender)

admin.site.register(TenderStatusHistory)
admin.site.register(BidStatusHistory)