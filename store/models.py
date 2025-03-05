from django.db import models

# Create your models here.
from django.db import models


class Item(models.Model):
    """
    Model for store items as specified in the task.
    """
    title = models.CharField(max_length=255, verbose_name='Наименование')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Receipt(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    items = models.ManyToManyField(Item, through='ReceiptItem', verbose_name='Товары')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Итоговая сумма')
    pdf_file = models.FileField(upload_to='receipts/', blank=True, null=True, verbose_name='PDF файл')
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True, verbose_name='QR-код')

    def __str__(self):
        return f'Чек #{self.id} от {self.created_at}'

    class Meta:
        verbose_name = 'Чек'
        verbose_name_plural = 'Чеки'


class ReceiptItem(models.Model):
    """
    Intermediate model for Receipt-Item relationship.
    """
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='receipt_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    def total_price(self):
        return self.item.price * self.quantity

    def __str__(self):
        return f'{self.item.title} x {self.quantity}'

    class Meta:
        verbose_name = 'Позиция чека'
        verbose_name_plural = 'Позиции чека'