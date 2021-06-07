from .models import Category

def main_link(request):
    links = Category.objects.all()
    return dict(links=links)