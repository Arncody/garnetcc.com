"""
website/urls.py
وظیفه: مسیرهای مربوط به اپلیکیشن website (صفحه اصلی، جزئیات پروژه، robots.txt).
"""
from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    path("", views.home, name="home"),
    path("projects/", views.projects_list, name="projects_list"),
    path("projects/<str:slug>/", views.project_detail, name="project_detail"),
    path("language/", views.set_language, name="set_language"),
    path("newsletter/subscribe/", views.subscribe_newsletter, name="newsletter_subscribe"),
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/<str:slug>/", views.blog_detail, name="blog_detail"),
    path("favicon.ico", views.favicon_ico, name="favicon"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
]
