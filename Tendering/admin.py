from django.contrib import admin
from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']


@admin.register(TenderAttachment)
class TenderAttachmentAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']


@admin.register(BidDocument)
class BidDocumentAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']


@admin.register(SavedTender)
class SavedTenderAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']


@admin.register(CategoryCompany)
class CategoryCompanyAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']


@admin.register(CategoryTender)
class CategoryTenderAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']


@admin.register(TenderStatusHistory)
class TenderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']


@admin.register(BidStatusHistory)
class BidStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']

@admin.register(Notification)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']
