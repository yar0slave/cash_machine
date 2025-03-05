from rest_framework import serializers
from .models import Item, Receipt, ReceiptItem


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'title', 'price']


class ReceiptItemSerializer(serializers.ModelSerializer):
    item_details = ItemSerializer(source='item', read_only=True)

    class Meta:
        model = ReceiptItem
        fields = ['item', 'quantity', 'item_details']


class ReceiptSerializer(serializers.ModelSerializer):
    items = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    receipt_items = ReceiptItemSerializer(many=True, read_only=True)
    qr_code_url = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Receipt
        fields = ['id', 'created_at', 'total_amount', 'items', 'receipt_items', 'qr_code_url', 'pdf_url']
        read_only_fields = ['created_at', 'total_amount', 'qr_code_url', 'pdf_url']

    def get_qr_code_url(self, obj):
        if obj.qr_code:
            return obj.qr_code.url
        return None

    def get_pdf_url(self, obj):
        if obj.pdf_file:
            return obj.pdf_file.url
        return None
