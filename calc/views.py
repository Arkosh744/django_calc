# Create your views here.
from django.http import HttpResponse
from django.urls import reverse


def thermal(request):
    url = reverse('thermal')
    print(url)
    return HttpResponse('thermal')


def barrel(request):
    return HttpResponse('barrel')


def forming(request):
    return HttpResponse('forming')
