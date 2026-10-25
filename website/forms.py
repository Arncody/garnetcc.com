"""
website/forms.py
وظیفه: فرم درخواست مشاوره + اعتبارسنجی سمت سرور + Honeypot ضد اسپم.
"""
import re
from django import forms
from .models import ConsultationRequest

PHONE_RE = re.compile(r"^0(9\d{9}|\d{2,3}\d{7,8})$")


class ConsultationForm(forms.ModelForm):
    def __init__(self, *args, language="fa", texts=None, **kwargs):
        super().__init__(*args, **kwargs)
        # عنوان فیلدها، راهنماها و گزینه‌ها از پنل ادمین (متن‌های عنوان‌ها و فرم) خوانده می‌شود.
        if texts is None:
            from .models import SiteTexts
            texts = SiteTexts.load().resolve(language)
        self.fields["name"].label = texts["label_name"]
        self.fields["gender"].label = texts["label_gender"]
        self.fields["phone"].label = texts["label_phone"]
        self.fields["subject"].label = texts["label_subject"]
        self.fields["message"].label = texts["label_message"]
        self.fields["name"].widget.attrs["placeholder"] = texts["ph_name"]
        self.fields["phone"].widget.attrs["placeholder"] = texts["ph_phone"]
        self.fields["subject"].widget.attrs["placeholder"] = texts["ph_subject"]
        self.fields["message"].widget.attrs["placeholder"] = texts["ph_message"]
        self.fields["gender"].choices = [
            ("male", texts["opt_male"]),
            ("female", texts["opt_female"]),
            ("other", texts["opt_other"]),
        ]
    # فیلد Honeypot: برای کاربر واقعی مخفی است؛ ربات‌ها معمولاً آن را پر می‌کنند.
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
        label="",
    )

    class Meta:
        model = ConsultationRequest
        fields = ["name", "gender", "phone", "subject", "message"]
        widgets = {
            "gender": forms.RadioSelect(attrs={"class": "gender-options"}),
            "name": forms.TextInput(attrs={
                "class": "form-control", "maxlength": 100, "placeholder": "مثال: مهندس رادمنش", "required": True,
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control", "maxlength": 20, "placeholder": "۰۹۱۲XXXXXXX", "required": True,
                "inputmode": "numeric",
            }),
            "subject": forms.TextInput(attrs={"class":"form-control","maxlength":150,"placeholder":"موضوع درخواست / Project subject", "required": True}),
            "message": forms.Textarea(attrs={
                "class": "form-control", "maxlength": 1000, "rows": 4,
                "placeholder": "نوع پروژه، منطقه، متراژ یا سوال مورد نظر...",
            }),
        }
        labels = {
            "gender": "عنوان",
            "name": "نام و نام‌خانوادگی",
            "phone": "شماره تماس همراه",
            "message": "توضیحات یا خلاصه پروژه (اختیاری)",
        }

    def clean_website(self):
        """اگر فیلد Honeypot مقدار داشته باشد، درخواست ربات تلقی می‌شود."""
        value = self.cleaned_data.get("website")
        if value:
            raise forms.ValidationError("درخواست نامعتبر است.")
        return value

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if len(name) < 2:
            raise forms.ValidationError("نام معتبر وارد کنید.")
        return name

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        phone = phone.replace(" ", "").replace("-", "")
        if not PHONE_RE.match(phone):
            raise forms.ValidationError("شماره تماس معتبر وارد کنید (مثال: 09123456789).")
        return phone


class NewsletterSubscriptionForm(forms.Form):
    email = forms.EmailField(
        label="ایمیل",
        max_length=254,
        widget=forms.EmailInput(attrs={
            "class": "newsletter-email",
            "placeholder": "ایمیل شما" ,
            "autocomplete": "email",
            "inputmode": "email",
            "required": True,
            "maxlength": 254,
        }),
    )
    website = forms.CharField(required=False, widget=forms.HiddenInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    def clean_email(self):
        return (self.cleaned_data.get("email") or "").strip().lower()

    def clean_website(self):
        value = self.cleaned_data.get("website")
        if value:
            raise forms.ValidationError("درخواست نامعتبر است.")
        return value
