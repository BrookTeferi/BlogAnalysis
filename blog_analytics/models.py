from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)
    
    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['country', 'is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.username


class Blog(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blogs'
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blogs',
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', 'created_at']),
            models.Index(fields=['country', 'created_at']),
            models.Index(fields=['created_at', 'is_published']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.title


class BlogView(models.Model):
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        related_name='views'
    )
    viewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='viewed_blogs'
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blog_views'
    )
    viewed_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['blog', 'viewed_at']),
            models.Index(fields=['viewer', 'viewed_at']),
            models.Index(fields=['country', 'viewed_at']),
            models.Index(fields=['viewed_at']),
            models.Index(fields=['country', 'blog']),
            models.Index(fields=['viewer', 'blog']),
        ]
    
    def __str__(self):
        viewer_name = self.viewer.username if self.viewer else "Anonymous"
        return f"{viewer_name} viewed {self.blog.title} at {self.viewed_at}"
