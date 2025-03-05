from django.contrib import admin
from .models import Item, Receipt, ReceiptItem

class ReceiptItemInline(admin.TabularInline):
    model = ReceiptItem
    extra = 1

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price')
    search_fields = ('title',)

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'total_amount')
    inlines = [ReceiptItemInline]
    readonly_fields = ('created_at', 'total_amount', 'pdf_file', 'qr_code')