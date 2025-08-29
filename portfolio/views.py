from django.shortcuts import render


def portfolio_index(request):
    return render(request, 'portfolio/index.html')


def projects_list(request):
    return render(request, 'portfolio/projects.html')

# Create your views here.
