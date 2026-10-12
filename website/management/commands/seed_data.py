"""
website/management/commands/seed_data.py
وظیفه: پر کردن اولیه دیتابیس با محتوای معرفی‌شده در بریف پروژه (تنظیمات سایت،
Hero + آمار، خدمات، پروژه‌های انجام‌شده و در حال اجرا با گالری دسته‌بندی‌شده،
بخش‌های About/فلسفه ساخت/CTA و ویژگی‌های فلسفه ساخت).
اجرا: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from website.models import (
    SiteSettings, HeroSection, HeroStat, Project, ProjectImage,
    SiteSection, PhilosophyFeature,
)


class Command(BaseCommand):
    help = "پر کردن اولیه دیتابیس با محتوای نمونه گارنت"

    def handle(self, *args, **options):
        settings_obj = SiteSettings.load()
        settings_obj.brand_name = "گارنت"
        settings_obj.legal_name = "بهمن ساختار آوید"
        settings_obj.phone = "02634019271"
        settings_obj.email = "garnet-group3@gmail.com"
        settings_obj.address = "البرز، کرج، گوهردشت، بلوار اصلی، مجتمع تجاری اداری نیکامال"
        settings_obj.instagram_url = "https://instagram.com/garnet_cc"
        settings_obj.booking_url = "#contact"
        settings_obj.working_hours_weekday = "۹:۰۰ الی ۱۸:۰۰"
        settings_obj.working_hours_weekend = "۹:۰۰ الی ۱۳:۰۰"
        settings_obj.tagline_en = "A refined approach to contemporary residential architecture, engineering and development by Garnet."
        settings_obj.tagline = (
            "«گارنت» با پشتوانه رسمی شرکت بهمن ساختار آوید؛ در طراحی و اجرای آپارتمان‌های مدرن "
            "و فاخر مسکونی، خوش‌پلان و لوکس با تکیه بر اصالت مهندسی و سادگی معاصر."
        )
        settings_obj.meta_title = "گارنت | بهمن ساختار آوید"
        settings_obj.meta_description = "گارنت، آفرینش آپارتمان‌های فاخر و معماری اصیل معاصر با پشتوانه رسمی شرکت بهمن ساختار آوید."
        settings_obj.save()

        hero = HeroSection.load()
        hero.badge_text = "طراحی و ساخت تخصصی ابنیه مدرن | شرکت بهمن ساختار آوید"
        hero.badge_text_en = "CONTEMPORARY ARCHITECTURE · ENGINEERING · DEVELOPMENT"
        hero.title = "گارنت؛ آفرینش آپارتمان‌های فاخر و معماری اصیل معاصر"
        hero.title_en = "Garnet — Contemporary residences, crafted with precision"
        hero.subtitle_en = "A refined harmony of light, proportion and enduring materials. Garnet creates contemporary residential architecture backed by disciplined engineering and delivery."
        hero.subtitle = (
            "همنشینی هارمونیک نور، فضا و متریال ناب در ساختمان‌ها و واحدهای مسکونی مدرن. برند «گارنت» "
            "با تمرکز انحصاری بر احداث پروژه‌های لوکس و با پشتوانه رسمی شرکت ثبتی «بهمن ساختار آوید»، "
            "سازه‌هایی ماندگار و با اصالت مهندسی خلق می‌کند."
        )
        hero.primary_button_text = "پروژه‌های در حال اجرا"
        hero.primary_button_text_en = "Current developments"
        hero.primary_button_url = "#ongoing-projects"
        hero.secondary_button_text = "نمونه‌کارهای اجرا شده"
        hero.secondary_button_text_en = "Built portfolio"
        hero.secondary_button_url = "#showcase"
        hero.tertiary_button_text = "تماس و مشاوره"
        hero.tertiary_button_text_en = "Private consultation"
        hero.tertiary_button_url = "#contact"
        hero.save()

        for stat in list(hero.stats.all()):
            stat.delete()
        hero_stats = [
            ("مدرن و پایدار", "سبک انحصاری طراحی"),
            ("درجه‌یک", "اصالت متریال و سازه"),
            ("۱۰۰٪", "نظارت عالیه مهندسی"),
        ]
        for order, (value, label) in enumerate(hero_stats, start=1):
            HeroStat.objects.create(hero=hero, value=value, label=label, order=order)

        SiteSection.objects.update_or_create(
            key=SiteSection.KEY_ABOUT,
            defaults=dict(
                title="درباره گارنت",
                title_en="About Garnet",
                subtitle="درباره ما",
                subtitle_en="A contemporary residential architecture studio",
                content_en="Garnet is the residential development brand of Bahman Sakhtar Avid, focused on contemporary, high-quality homes with disciplined engineering and transparent delivery.",
                content=(
                    "گارنت برند ساختمانی رسمی شرکت بهمن ساختار آوید است که با تمرکز انحصاری بر طراحی و "
                    "اجرای آپارتمان‌های مدرن و لوکس مسکونی فعالیت می‌کند؛ مجموعه‌ای که با تکیه بر دانش فنی، "
                    "تجربه اجرایی و پایبندی کامل به تعهدات حقوقی، پروژه‌های متعددی را با کیفیت و در زمان "
                    "مقرر به بهره‌برداری رسانده است."
                ),
                is_active=True,
                order=1,
            ),
        )
        why_section, _ = SiteSection.objects.update_or_create(
            key=SiteSection.KEY_WHY_GARNET,
            defaults=dict(
                title="فلسفه طراحی و اصالت ساخت",
                title_en="Design philosophy & construction integrity",
                subtitle="اصالت، کیفیت و تمایز در ساخت",
                subtitle_en="Precision, restraint and enduring quality",
                content=(
                    "در «گارنت»، تخصص ما منحصراً بر آفرینش آپارتمان‌های مدرن و لوکس مسکونی متمرکز است؛ "
                    "فضاهایی با پلان‌های مهندسی‌شده، نور سرشار و همنشینی متریال طبیعی که آرامش زندگی "
                    "حقیقی را رقم می‌زنند."
                ),
                content_en="Our work is shaped by calm proportions, natural light, durable materials and meticulous execution.",
                quote_text_en="Luxury in a residence is not excess; it is the harmony of proportion, light and everyday comfort.",
                quote_author_en="Garnet · Bahman Sakhtar Avid",
                quote_text=(
                    "زیبایی آپارتمان مدرن در هماهنگی با آرامش زیستن است؛ ما در گارنت خانه‌هایی می‌سازیم "
                    "که هر روز زندگی در آن‌ها ارزشمند و الهام‌بخش باشد."
                ),
                quote_author="برند ساختمانی گارنت | شرکت بهمن ساختار آوید",
                is_active=True,
                order=2,
            ),
        )
        SiteSection.objects.update_or_create(
            key=SiteSection.KEY_CTA,
            defaults=dict(
                title="آماده شروع پروژه بعدی هستید؟",
                title_en="Ready to shape the next address?",
                content="برای دریافت مشاوره رایگان درباره پروژه ساختمانی خود، فرم زیر را تکمیل کنید یا مستقیم با ما تماس بگیرید.",
                content_en="Tell us about your project and our team will contact you for a private consultation.",
                is_active=True,
                order=3,
            ),
        )

        PhilosophyFeature.objects.all().delete()
        philosophy = [
            ("🛡", "پشتوانه رسمی و حقوقی",
             "کلیه قراردادها، پیش‌فروش‌ها و تعهدات اجرایی تحت نظارت مستقیم شرکت ثبتی بهمن ساختار آوید "
             "(سهامی خاص) با شفافیت کامل حقوقی و مهندسی منعقد می‌گردد."),
            ("✨", "متریال پایدار و مشاعات مجلل",
             "لابی‌های مبله با گرین‌وال طبیعی، سنگ‌های اسلب بوک‌مچ، آسانسورهای پیشرفته، شیرآلات توکار و "
             "سیستم‌های سرمایش-گرمایش مدرن در کلیه واحدها."),
            ("📐", "پلان‌های ژورنالی و بی‌نقص",
             "طراحی اختصاصی برای آپارتمان‌های مسکونی؛ تفکیک هوشمندانه بخش عمومی از خصوصی، حذف فضای پرتی "
             "و حداکثر بهره‌برداری از نور طبیعی روز."),
        ]
        for order, (icon, title, desc) in enumerate(philosophy, start=1):
            en = {"پشتوانه رسمی و حقوقی": ("Formal & legal backing", "Contracts and commitments are handled with transparent engineering and formal legal oversight."), "متریال پایدار و مشاعات مجلل": ("Enduring materials & refined amenities", "Natural materials, considered common spaces and modern building systems create a lasting residential experience."), "پلان‌های ژورنالی و بی‌نقص": ("Editorial-grade planning", "Efficient layouts, generous daylight and a clear separation between public and private living zones.")}[title]
            PhilosophyFeature.objects.create(icon_glyph=icon, title=title, title_en=en[0], description=desc, description_en=en[1], order=order)

        completed_data = [
            dict(title="گارنت ۱۵", code="G-15", location="کرج، گوهردشت", year=1403),
            dict(title="گارنت ۱۳", code="G-13", location="کرج، گوهردشت", year=1402),
            dict(title="گارنت ۱۰", code="G-10", location="کرج، گوهردشت", year=1401),
        ]
        # پیشنهاد عنوان/توضیح/دسته‌بندی تصاویر گالری هر پروژه (برای راهنمایی هنگام آپلود دستی از پنل ادمین،
        # چون ProjectImage نیازمند فایل واقعی تصویر است و در Seed خودکار قابل تولید نیست):
        # نمای بیرونی، لابی و گرین‌وال، پاگرد آسانسور، راه‌پله، پذیرایی، آشپزخانه، اتاق خواب، سرویس.
        for order, data in enumerate(completed_data, start=1):
            Project.objects.update_or_create(
                slug=slugify("garnet-" + data["code"], allow_unicode=True),
                defaults=dict(
                    title=data["title"], code=data["code"], status=Project.STATUS_COMPLETED,
                    location=data["location"], year=data["year"],
                    short_description=f"پروژه {data['title']} یکی از نمونه‌کارهای اجراشده هلدینگ ساختمانی گارنت در {data['location']}.",
                    order=order, is_active=True,
                ),
            )

        ongoing_data = [
            dict(
                title="گارنت میدو (Garnet Meadow)", code="G-MEADOW", location="البرز، باغستان کرج",
                is_featured=True, order=1, status_note="اجرای اسکلت و محوطه‌سازی",
                badge_text="بزرگ‌ترین پروژه ساختمانی مجموعه گارنت",
                short_description="ابرپروژه گارنت میدو | بزرگ‌ترین مجموعه ساختمانی گارنت در باغستان",
                full_description=(
                    "«گارنت میدو» در نگین سرسبز باغستان کرج، یکی از باشکوه‌ترین و عظیم‌ترین پروژه‌های "
                    "هلدینگ گارنت به‌شمار می‌آید. این مجتمع مسکونی رویایی، ترکیبی از طبیعت کم‌نظیر، "
                    "ابعاد وسیع، مشاعات استثنایی و معماری هتلینگ مدرن را در مقایسه کم‌نظیری پیش روی "
                    "خریداران نخبه قرار می‌دهد."
                ),
                feature_list=(
                    "یکی از بزرگ‌ترین، باشکوه‌ترین و گسترده‌ترین پروژه‌های در حال ساخت گارنت\n"
                    "موقعیت استراتژیک در باغستان کرج با اقلیم پاک، هوای ییلاقی و افق دید کوهستان\n"
                    "محوطه‌سازی سبز وسیع، روف‌گاردن چهارفصل و مسیرهای تندرستی اختصاصی\n"
                    "لابی بسیار وسیع با سقف دوپل، فضاهای تعاملی و کافی‌بار اختصاصی ساکنین\n"
                    "ارزش افزوده تضمین‌شده و چشم‌انداز اقتصادی فوق‌العاده برای سرمایه‌گذاران"
                ),
                cta_text="اطلاعات و پیش‌خرید",
            ),
            dict(
                title="گارنت ۲۶", code="G-26", location="البرز، گوهردشت کرج",
                is_featured=False, order=2, status_note="پیشرفت عملیات اجرایی",
                short_description="پروژه مدرن گارنت ۲۶ با رویکرد مینیمال و خطوط خالص معماری.",
                full_description=(
                    "این عمارت مسکونی متکی بر آرامش زیست و ظرافت اجرایی، مهندسی ناب که در قلب "
                    "گوهردشت کرج استوار می‌گردد."
                ),
                feature_list=(
                    "طراحی دلوکه با تابش مستقیم نور طبیعی خورشید به تمام واحدها\n"
                    "متریال برند در بخش شیرآلات، اتصالات، درب‌ها و کابینت‌ها\n"
                    "پارکینگ‌های چشم‌نواز استاندارد با رمپ استاندارد و تهویه اگزاست قوی"
                ),
            ),
            dict(
                title="لاوان (Lavan)", code="G-27", location="البرز، گوهردشت کرج",
                is_featured=False, order=3, status_note="تکمیل اسکلت و اجرای تاسیسات",
                short_description="پروژه شیک گارنت ۲۷ در موقعیتی آرام و اصیل از اعیان‌نشین گوهردشت.",
                full_description="طراحی متکی بر تلفیق هنر آونگارد، بهینه‌سازی حداکثری انرژی و مشاعات فاخر.",
                feature_list=(
                    "واقع در دنج‌ترین کوچه اعیان‌نشین گوهردشت با امنیت پایدار\n"
                    "معماری پایدار با پنجره‌های عایق صوت و حرارت ترمال‌بریک\n"
                    "مشاعات چشم‌نواز شامل سالن اجتماعات، روف‌گاردن و پارکینگ‌های اختصاصی"
                ),
            ),
            dict(
                title="آترون (Atron)", code="G-28", location="البرز، گوهردشت کرج",
                is_featured=False, order=4, status_note="سازه و اجرای مهندسی مدرن",
                short_description="پروژه فاخر گارنت ۲۸ (آترون)؛ نگینی تازه از اعیان‌نشین گوهردشت کرج.",
                full_description=(
                    "این پروژه با تلفیق هنر آوانگارد و بالاترین استانداردهای ایمنی سازه و متریال "
                    "سفارشی وارداتی، تجربه‌ای بی‌بدیل از زندگی مدرن را بازتعریف می‌کند."
                ),
                feature_list=(
                    "موقعیت ممتاز در گوهردشت کرج با دسترسی شاهراهی عالی\n"
                    "لابی مجلل با طراحی هتلینگ ۵ ستاره و فضای تشریفات\n"
                    "پلان‌های مهندسی‌شده با نورگیری سرتاسری و بالکن‌های دلباز"
                ),
            ),
        ]
        for data in ongoing_data:
            data = dict(data)
            title = data.pop("title")
            code = data.pop("code")
            Project.objects.update_or_create(
                slug=slugify("garnet-" + code, allow_unicode=True),
                defaults=dict(title=title, code=code, status=Project.STATUS_ONGOING, is_active=True, **data),
            )

        project_en = {
            "G-15": ("Garnet 15", "Karaj · Gohardasht"), "G-13": ("Garnet 13", "Karaj · Gohardasht"), "G-10": ("Garnet 10", "Karaj · Gohardasht"),
            "G-MEADOW": ("Garnet Meadow", "Alborz · Baghestan, Karaj"), "G-26": ("Garnet 26", "Alborz · Gohardasht, Karaj"), "G-27": ("Lavan", "Alborz · Gohardasht, Karaj"), "G-28": ("Atron", "Alborz · Gohardasht, Karaj"),
        }
        for project in Project.objects.all():
            if project.code in project_en:
                project.title_en, project.location_en = project_en[project.code]
                project.short_description_en = f"{project.title_en} — a Garnet residential development shaped around contemporary planning and precise execution."
                project.full_description_en = project.full_description or project.short_description_en
                project.feature_list_en = "Crafted with disciplined engineering\nContemporary residential planning\nHigh-quality materials and common areas"
                project.badge_text_en = "SIGNATURE GARNET DEVELOPMENT" if project.is_featured else project.badge_text_en
                project.cta_text_en = "Project details & availability"
                project.status_note_en = "Construction in progress"
                project.save()

        self.stdout.write(self.style.SUCCESS(
            "محتوای اولیه گارنت با موفقیت ثبت شد. اکنون تصاویر واقعی را از پنل ادمین برای هر پروژه/خدمت آپلود کنید."
        ))
