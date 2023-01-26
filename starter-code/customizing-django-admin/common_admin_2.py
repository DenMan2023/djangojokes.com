from django.conf import settings
from django.contrib import admin
from django.db.models import TextField
from django.forms import Textarea

admin.site.site_header = 'Django Jokes Admin'

class DjangoJokesAdmin(admin.ModelAdmin):
    # List Attributes
    list_per_page = 25
    list_max_show_all = 1000
    
    # Form Attributes
    save_as = True
    
    class Media:
        js = (
            settings.STATIC_URL + 'js/admin.js',
            'https://kit.fontawesome.com/f804978a2a.js'
        )    
        css = {
             'all': (settings.STATIC_URL + 'css/admin.css',)
        }