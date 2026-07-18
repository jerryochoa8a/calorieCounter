from django.shortcuts import render

posts = [
    {
        'author': 'Jared Brinas',
        'title' : 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'July 6, 2026'
    },
    {
        'author': 'Jane Doe',
        'title' : 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'July 6, 2026'
    }
]


def home(request):
    context = {
        'posts': posts
    }
    return render(request, 'blog/home.html', context)

def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})                        

