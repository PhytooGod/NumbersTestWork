from rest_framework import serializers
from .models import Numbers

class NumbersSerializer(serializers.ModelSerializer):
	class Meta:
		model = Numbers
		fields = ['num', 'order_number', 'price_dollar', 'supply_date', 'price_ruble']