from .models import SiteSettings, SiteTheme, SiteTexts, CompanyCatalog
from .forms import ConsultationForm

def site_settings(request):
    lang = request.session.get("site_lang", "fa")
    if lang not in {"fa", "en"}:
        lang = "fa"
    texts = SiteTexts.load().resolve(lang)
    return {
        "site_settings": SiteSettings.load(),
        "site_theme": SiteTheme.load(),
        "catalog": CompanyCatalog.objects.filter(is_active=True).first(),
        "lang": lang,
        "is_en": lang == "en",
        "T": texts,
        "consultation_form": ConsultationForm(language=lang, texts=texts),
    }
