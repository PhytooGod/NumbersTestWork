from django.urls import path, include
from .views import NumbersDetail, NumbersList

urlpatterns = [
	path('numbers/<int:num>', NumbersDetail.as_view(), name='numbersDetail'),
    path('numbers/', NumbersList.as_view(), name='numbersList'),
]