from django.db import models

# Create your models here.
class Numbers(models.Model):
	num = models.IntegerField()
	order_number = models.IntegerField()
	price_dollar = models.FloatField()
	supply_date = models.DateField()
	price_ruble = models.FloatField()

	def to_json(self):
		return {
			'num': self.num,
			'order_number': self.order_number,
			'price_dollar': self.price_dollar,
			'supply_date': self.supply_date,
			'price_ruble': self.price_ruble,
		}