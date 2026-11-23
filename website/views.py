"""
website/views.py
وظیفه: نمایش صفحه اصلی (تک‌صفحه‌ای)، صفحه جزئیات پروژه و پردازش امن فرم مشاوره.
"""
from unicodedata import category, normalize

from django.conf import settings
from django.core.cache import cache
from django.db.models import prefetch_related_objects
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.utils.http import url_has_allowed_host_and_scheme

from .models import HeroSection, Project, SiteSection, PhilosophyFeature, CompanyCatalog, SiteTexts, NewsletterSubscriber
from .forms import ConsultationForm, NewsletterSubscriptionForm

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


def _mixed_home_projects(limit=24):
    """همه‌ی پروژه‌های فعال برای ردیف چرخان صفحه اصلی (به‌صورت یکی‌درمیان در حال اجرا / اتمام‌شده)."""
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
    home_projects = _mixed_home_projects()
    about_section = SiteSection.objects.filter(key=SiteSection.KEY_ABOUT, is_active=True).first()
    # پس‌زمینه درباره فقط از تصویر اختصاصی همان بخش می‌آید؛ تصویر پروژه‌ها fallback نیست.
    about_bg = about_section.image if about_section and about_section.image else None

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



@require_http_methods(["POST"])
def subscribe_newsletter(request):
    """Validate and store newsletter emails; duplicate submissions are idempotent."""
    ip_address = _get_client_ip(request)
    if ip_address:
        key = f"newsletter_rl_{ip_address}"
        count = cache.get(key, 0)
        if count >= 5:
            messages.error(request, "تعداد تلاش‌ها زیاد است؛ لطفاً کمی بعد دوباره امتحان کنید." if request.session.get("site_lang", "fa") != "en" else "Too many attempts. Please try again later.")
            return redirect("website:home")
        cache.set(key, count + 1, 60 * 60)
    form = NewsletterSubscriptionForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data["email"]
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email, defaults={"is_active": True}
        )
        if not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save(update_fields=["is_active", "updated_at"])
        if created:
            messages.success(request, "ایمیل شما با موفقیت در خبرنامه ثبت شد." if request.session.get("site_lang", "fa") != "en" else "Your email has been subscribed successfully.")
        else:
            messages.info(request, "این ایمیل قبلاً در خبرنامه ثبت شده است." if request.session.get("site_lang", "fa") != "en" else "This email is already subscribed.")
    else:
        messages.error(request, "لطفاً یک آدرس ایمیل معتبر وارد کنید." if request.session.get("site_lang", "fa") != "en" else "Please enter a valid email address.")
    referer = request.META.get("HTTP_REFERER", "")
    if referer and url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return HttpResponseRedirect(referer + ("#newsletter" if "#" not in referer else ""))
    return redirect("website:home")

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


def _editorial_sections(*keys):
    return SiteSection.objects.filter(key__in=keys, is_active=True).in_bulk(field_name="key")


def project_detail(request, slug):
    active = Project.objects.filter(is_active=True).prefetch_related("images")
    project = get_object_or_404(active, slug=slug)
    candidates = active.exclude(pk=project.pk)
    related_projects = list(candidates.filter(status=project.status)[:2])
    related_projects += list(candidates.exclude(status=project.status)[:1])
    section = SiteSection.KEY_PROJECT_DETAIL_CTA
    return render(request, "website/projects/detail.html", {
        "project": project,
        "gallery": project.images.all(),
        "related_projects": related_projects,
        "related_section": _editorial_sections(section).get(section),
    })


def about(request):
    sections = _editorial_sections(
        SiteSection.KEY_ABOUT_HERO, SiteSection.KEY_ABOUT_STORY, SiteSection.KEY_ABOUT_PHILOSOPHY,
        SiteSection.KEY_ABOUT_PRINCIPLES, SiteSection.KEY_ABOUT_QUOTE, SiteSection.KEY_ABOUT_CTA,
    )
    return render(request, "website/about.html", {
        "sections": sections,
        "principles": PhilosophyFeature.objects.filter(is_active=True),
    })


def robots_txt(request):
    from django.http import HttpResponse
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


_PROJECT_SEARCH_CHARACTERS = str.maketrans(
    {"ي": "ی", "ى": "ی", "ك": "ک", "\u200c": None, "\u200d": None, "ـ": None}
    | dict(zip("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789"))
)


def _project_search_text(text):
    text = normalize("NFKD", text).casefold().translate(_PROJECT_SEARCH_CHARACTERS)
    return "".join(" " if category(char).startswith("P") else char for char in text if category(char) != "Mn")


def projects_list(request):
    query = request.GET.get("q", "")[:100].strip()
    terms = _project_search_text(query).split()
    projects = list(Project.objects.filter(is_active=True))
    context = {}
    if terms:
        def matches(project):
            searchable = _project_search_text(" ".join((
                project.title, project.title_en, project.code, project.location, project.location_en,
            )))
            return all(term in searchable for term in terms)

        projects = [project for project in projects if matches(project)]
        context.update(project_query=query, search_results=projects)
    else:
        sections = _editorial_sections(SiteSection.KEY_PROJECTS_HERO, SiteSection.KEY_PROJECTS_NOTE)
        context.update(
            hero_section=sections.get(SiteSection.KEY_PROJECTS_HERO),
            note_section=sections.get(SiteSection.KEY_PROJECTS_NOTE),
            ongoing_projects=[project for project in projects if project.status == Project.STATUS_ONGOING],
            completed_projects=[project for project in projects if project.status == Project.STATUS_COMPLETED],
        )
    prefetch_related_objects(projects, "images")
    return render(request, "website/projects/list.html", context)


def favicon_ico(request):
    """/favicon.ico: گوگل و مرورگرها این مسیر را مستقیم درخواست می‌کنند."""
    from django.http import HttpResponseRedirect, Http404
    from .models import SiteSettings
    fav = SiteSettings.load().favicon
    if not fav:
        raise Http404
    return HttpResponseRedirect(fav.url)
