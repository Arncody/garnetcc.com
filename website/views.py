"""
website/views.py
وظیفه: نمایش صفحه اصلی (تک‌صفحه‌ای)، صفحه جزئیات پروژه و پردازش امن فرم مشاوره.
"""
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.utils.http import url_has_allowed_host_and_scheme

from .models import HeroSection, Project, SiteSection, PhilosophyFeature, CompanyCatalog, BlogPost, SiteTexts
from .forms import ConsultationForm

# محدودیت درخواست فرم مشاوره برای هر IP (ضد اسپم ساده، بدون نیاز به Redis)
RATE_LIMIT_MAX_REQUESTS = 3
RATE_LIMIT_WINDOW_SECONDS = 60 * 60  # ۱ ساعت


def _get_client_ip(request):
    # Never trust X-Forwarded-For from arbitrary clients: it is trivially spoofable.
    # Configure a trusted proxy at the host and explicitly opt in only if needed.
    if getattr(settings, "TRUST_PROXY_HEADERS", False):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded:
            return forwarded.split(",")[0].strip()[:64]
    return (request.META.get("REMOTE_ADDR") or "")[:64]


def _is_rate_limited(ip_address):
    if not ip_address:
        return False
    cache_key = f"consultation_rl_{ip_address}"
    count = cache.get(cache_key, 0)
    if count >= RATE_LIMIT_MAX_REQUESTS:
        return True
    cache.set(cache_key, count + 1, RATE_LIMIT_WINDOW_SECONDS)
    return False


def _mixed_home_projects(limit=3):
    """ترکیب پروژه‌های در حال اجرا و اتمام‌شده برای صفحه اصلی (به‌صورت یکی‌درمیان)."""
    base = Project.objects.filter(is_active=True).prefetch_related("images")
    pools = [
        list(base.filter(status=Project.STATUS_ONGOING)[:limit]),
        list(base.filter(status=Project.STATUS_COMPLETED)[:limit]),
    ]
    mixed, turn = [], 0
    while len(mixed) < limit and (pools[0] or pools[1]):
        pool = pools[turn % 2]
        if pool:
            mixed.append(pool.pop(0))
        turn += 1
    return mixed


def _common_context():
    ongoing_qs = Project.objects.filter(status=Project.STATUS_ONGOING, is_active=True).prefetch_related("images")
    completed_qs = (
        Project.objects.filter(status=Project.STATUS_COMPLETED, is_active=True)
        .prefetch_related("images")
    )
    hero = HeroSection.load()
    home_projects = _mixed_home_projects(3)
    about_section = SiteSection.objects.filter(key=SiteSection.KEY_ABOUT, is_active=True).first()
    # پس‌زمینه‌ی «درباره گارنت»: عکس همان بخش، وگرنه عکس هیرو، وگرنه عکس نخستین پروژه
    about_bg = None
    if about_section and about_section.image:
        about_bg = about_section.image
    elif hero.background_image:
        about_bg = hero.background_image
    elif home_projects:
        about_bg = home_projects[0].cover_image

    return {
        "hero": hero,
        "hero_stats": hero.stats.all(),
        "home_projects": home_projects,
        "about_bg": about_bg,
        "completed_projects": completed_qs,
        "ongoing_projects": ongoing_qs,
        "featured_project": ongoing_qs.filter(is_featured=True).first(),
        "other_ongoing_projects": ongoing_qs.filter(is_featured=False),
        "about_section": about_section,
        "why_section": SiteSection.objects.filter(key=SiteSection.KEY_WHY_GARNET, is_active=True).first(),
        "cta_section": SiteSection.objects.filter(key=SiteSection.KEY_CTA, is_active=True).first(),
        "philosophy_features": PhilosophyFeature.objects.filter(is_active=True),
        "catalog": CompanyCatalog.objects.filter(is_active=True).first(),
        "featured_blog": BlogPost.objects.filter(is_published=True, is_featured=True).first(),
        "latest_blog": BlogPost.objects.filter(is_published=True)[:3],
    }


@require_http_methods(["GET", "POST"])
def home(request):
    context = _common_context()

    if request.method == "POST":
        lang = request.session.get("site_lang", "fa")
        if lang not in {"fa", "en"}:
            lang = "fa"
        form = ConsultationForm(request.POST, language=lang, texts=SiteTexts.load().resolve(lang))
        ip_address = _get_client_ip(request)

        if _is_rate_limited(ip_address):
            messages.error(
                request,
                _("تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً کمی بعد دوباره تلاش کنید."),
            )
            context["form"] = form
            context["consult_keep_open"] = True
            return render(request, "website/home.html", context)

        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.ip_address = ip_address
            consultation.save()
            messages.success(request, _("درخواست مشاوره شما با موفقیت ثبت شد. به‌زودی با شما تماس می‌گیریم."))
            return redirect("website:home")

        messages.error(request, _("لطفاً خطاهای فرم را برطرف کنید."))
        context["form"] = form
        context["consult_keep_open"] = True
    else:
        context["form"] = ConsultationForm(language=request.session.get("site_lang", "fa"))

    return render(request, "website/home.html", context)


def set_language(request):
    lang = request.GET.get("lang", "fa")
    if lang not in {"fa", "en"}:
        lang = "fa"
    request.session["site_lang"] = lang
    referer = request.META.get("HTTP_REFERER", "")
    if referer and url_has_allowed_host_and_scheme(
        referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return HttpResponseRedirect(referer)
    return HttpResponseRedirect("/")


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, is_active=True)
    context = _common_context()
    context["project"] = project
    context["gallery"] = project.images.all()
    context["related_projects"] = (
        Project.objects.filter(is_active=True).exclude(pk=project.pk).prefetch_related("images")[:3]
    )
    return render(request, "website/projects/detail.html", context)


def robots_txt(request):
    from django.http import HttpResponse
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def projects_list(request):
    base = Project.objects.filter(is_active=True).prefetch_related("images")
    return render(request, "website/projects/list.html", {
        "ongoing_projects": base.filter(status=Project.STATUS_ONGOING),
        "completed_projects": base.filter(status=Project.STATUS_COMPLETED),
    })


def blog_list(request):
    posts = BlogPost.objects.filter(is_published=True)
    return render(request, "website/blog/list.html", {"posts": posts})


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return render(request, "website/blog/detail.html", {"post": post})


def favicon_ico(request):
    """/favicon.ico: گوگل و مرورگرها این مسیر را مستقیم درخواست می‌کنند."""
    from django.http import HttpResponseRedirect, Http404
    from .models import SiteSettings
    fav = SiteSettings.load().favicon
    if not fav:
        raise Http404
    return HttpResponseRedirect(fav.url)
