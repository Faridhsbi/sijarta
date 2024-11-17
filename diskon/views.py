from django.shortcuts import render

def discount_page(request):
    context = {}
    return render(request, "discount_page.html", context)
