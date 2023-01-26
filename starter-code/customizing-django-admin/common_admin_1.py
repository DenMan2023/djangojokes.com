from django.contrib import admin

admin.site.index_title = 'Home'
admin.site.site_title = 'Django Jokes Admin'
admin.site.site_header = 'Django Jokes Admin'

class DjangoJokesAdmin(admin.ModelAdmin):
    list_per_page = 25
    list_max_show_all = 1000