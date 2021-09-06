from django.db import models
from django.conf import settings


# Create your models here.
from mainapp.models import Product


class Order(models.Model):
    FORMING = "FM"
    SENT_TO_PROCEED = "STP"
    PROCEEDED = "PRD"
    PAID = "PD"
    READY = "RDY"
    CANCEL = "CNC"

    ORDER_STATUS_CHOICES = (
        (FORMING, "формируется"),
        (SENT_TO_PROCEED, "отправлен в обработку"),
        (PROCEEDED, "обрабатывается"),
        (PAID, "оплачен"),
        (READY, "готов к выдаче"),
        (CANCEL, "отменен"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, verbose_name="создан")
    updated = models.DateTimeField(auto_now=True, verbose_name="обновлен")
    status = models.CharField(choices=ORDER_STATUS_CHOICES, max_length=3, default=FORMING, verbose_name="статус")
    is_active = models.BooleanField(default=True, verbose_name="активен")

    class Meta:
        ordering = ("-created",)
        verbose_name = "заказ"
        verbose_name_plural = "заказы"

    def __str__(self):
        return f"Текущий заказ: {self.pk}"

    def get_total_quantity(self):
        items = self.orderitems.select_related()
        return sum(list(map(lambda x: x.quantity, items)))

    def get_product_type_quantity(self):
        items = self.orderitems.select_related()
        return len(items)

    def get_total_cost(self):
        items = self.orderitems.select_related()
        return sum(list(map(lambda x: x.quantity * x.product.price, items)))

    def delete(self):
        for item in self.orderitems.select_related():
            item.product.quantity += item.quantity
            item.product.save()

        self.is_active = False
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="orderitems", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="продукт", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0, verbose_name="количество")

    def get_product_cost(self):
        return self.product.price * self.quantity





