from django.views.generic import TemplateView

class FilterView(TemplateView):
    template_name = 'practice/filters.html'


class HomePageView(TemplateView):
    template_name = 'home.html'


class TagView(TemplateView):
    template_name = 'practice/tags.html'