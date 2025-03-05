import os
import qrcode
from io import BytesIO
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from pdfkit.configuration import Configuration
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Item, Receipt, ReceiptItem
from .serializers import ReceiptSerializer

import pdfkit
from django.core.files.base import ContentFile

from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


class CashMachineView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ReceiptSerializer(data=request.data)

        if serializer.is_valid():
            receipt = Receipt.objects.create(total_amount=0)

            total_amount = 0
            item_ids = serializer.validated_data.get('items', [])
            receipt_items = []

            for item_id in item_ids:
                try:
                    item = Item.objects.get(id=item_id)
                    receipt_item = ReceiptItem.objects.create(
                        receipt=receipt,
                        item=item,
                        quantity=1
                    )
                    receipt_items.append(receipt_item)
                    total_amount += item.price
                except Item.DoesNotExist:
                    receipt.delete()
                    return Response(
                        {'error': f'Item with id {item_id} does not exist.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            receipt.total_amount = total_amount
            receipt.save()
            html_string = render_to_string('receipt.html', {
                'receipt': receipt,
                'receipt_items': receipt_items,
                'unique_id': f'{receipt.id:08d}# 05970'
            })

            config = Configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
            pdf_content = pdfkit.from_string(html_string, False, configuration=config)

            file_name = f'receipt_{receipt.id}.pdf'
            receipt.pdf_file.save(file_name, ContentFile(pdf_content))

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )

            pdf_url = request.build_absolute_uri(f'/media/receipts/{file_name}')
            qr.add_data(pdf_url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            qr_buffer = BytesIO()
            img.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)
            qr_file_name = f'qr_receipt_{receipt.id}.png'
            receipt.qr_code.save(qr_file_name, ContentFile(qr_buffer.getvalue()))
            qr_buffer.seek(0)
            return HttpResponse(qr_buffer.getvalue(), content_type='image/png')

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MediaFileView(APIView):

    def get(self, request, file_name, *args, **kwargs):
        file_path = os.path.join(settings.MEDIA_ROOT, 'receipts', file_name)

        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename={file_name}'
                return response

        return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
