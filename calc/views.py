# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse


def thermal(request):
    url = reverse('thermal')
    print(url)
    return render(request, 'calc/thermal.html')


def barrel(request):
    return render(request, 'calc/barrel.html')


def forming(request):
    return render(request, 'calc/forming.html')
