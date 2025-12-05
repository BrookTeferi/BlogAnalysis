from django.contrib import admin
from .models import Country, User, Blog, BlogView


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'country', 'is_active', 'created_at']
    list_filter = ['is_active', 'country', 'created_at']
    search_fields = ['username', 'email']
    date_hierarchy = 'created_at'


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'country', 'is_published', 'created_at']
    list_filter = ['is_published', 'country', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    date_hierarchy = 'created_at'
    raw_id_fields = ['author']


@admin.register(BlogView)
class BlogViewAdmin(admin.ModelAdmin):
    list_display = ['blog', 'viewer', 'country', 'viewed_at']
    list_filter = ['country', 'viewed_at']
    search_fields = ['blog__title', 'viewer__username']
    date_hierarchy = 'viewed_at'
    raw_id_fields = ['blog', 'viewer']
