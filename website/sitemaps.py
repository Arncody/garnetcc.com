"""
website/sitemaps.py
وظیفه: تولید sitemap.xml شامل صفحه اصلی و صفحات جزئیات پروژه‌ها (برای SEO).
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Project


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = "weekly"

    def items(self):
        return ["website:home", "website:projects_list", "website:blog_list"]

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Project.objects.filter(is_active=True)

    def location(self, obj):
        return obj.get_absolute_url()
