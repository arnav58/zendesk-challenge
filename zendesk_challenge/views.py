from django.shortcuts import render


def index(request):
    context = {
        'title': 'Latest Posts'
    }

    return render(request, 'zendesk_challenge/index.html', context)
