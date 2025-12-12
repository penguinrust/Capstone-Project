from django.views.generic import TemplateView


class HomePage(TemplateView):
    """
    Display the home page
    """
    template_name = 'index.html'
