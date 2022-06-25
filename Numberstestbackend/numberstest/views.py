from django.shortcuts import render
from django.http import Http404, JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Numbers
from .serializers import NumbersSerializer
import json

class NumbersList(APIView):
	def get(self, request):
		numbers = Numbers.objects.all()
		numbers = NumbersSerializer(numbers, many=True)
		return JsonResponse(numbers.data, safe=False)

	def post(self, request):
		data = json.loads(request.body)
		try:
			numbers = Numbers.objects.create(
				num=data['num'],
				order_number=data['order_number'],
				price_dollar=data['price_dollar'],
				supply_date=data['supply_date'],
				price_ruble=data['price_ruble']
			)
		except Exception as e:
			return JsonResponse({'message': str(e)}, status=400)
		return JsonResponse(numbers.to_json(), status=200)

class NumbersDetail(APIView):
	def get_object(self, num):
		try:
			return Numbers.objects.get(num=num)
		except Numbers.DoesNotExist as e:
			raise Http404

	def get(self, request, num=None):
		numbers = self.get_object(num=num)
		numbers = NumbersSerializer(numbers)
		return JsonResponse(numbers.data)

	def put(self, request, num=None):
		numbers = self.get_object(num)
		numbers = NumbersSerializer(instance=numbers, data=request.data)
		if numbers.is_valid():
			numbers.save()
			return Response(numbers.data)
		return Response(numbers.errors)

	def delete(self, request, num=None):
		numbers = self.get_object(num)
		numbers.delete()
		return Response({'message': 'deleted'}, status=204)