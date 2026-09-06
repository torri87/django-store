from django.http import JsonResponse
from .models import Item
from django.shortcuts import render

def get_items(request):
    items = Item.objects.all()
    data = [{"id": i.id, "name": i.name} for i in items]
    return JsonResponse(data, safe=False)


def items_page(request):
    return render(request, 'store/index.html')