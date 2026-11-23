# Project map (verified from GARNET.zip)

- `config/settings.py`: Django configuration, DB switch SQLite/PostgreSQL, security, static/media, cache.
- `config/urls.py`: root routes, admin, sitemap, protected-media route.
- `website/models.py`: data models and singleton configuration objects.
- `website/views.py`: homepage and server-rendered pages, consultation, newsletter, language selection.
- `website/urls.py`: public routes.
- `website/forms.py`: forms and validation.
- `website/admin.py`: editable CMS/admin experience.
- `website/context_processors.py`: global template context.
- `website/theme_tokens.py`: theme tokens/visual settings.
- `website/media_views.py`, `website/storage.py`: media delivery/storage behavior.
- `website/sitemaps.py`: sitemap generation.
- `website/migrations/0001..0021`: schema history, including the article archive and editable portfolio/About content, search labels and catalogue visibility.
- `templates/website/`: shared shell, home, About, project pages and cards.
- `static/css/`: style.css, garnet-ui.css, admin styles and others.
- `static/js/main.js`: frontend behavior; additional admin scripts.
- `docs/`: previous UI/image specifications and change logs.
- `requirements.txt`: Django 5.2.6, Pillow 11.3.0, python-decouple 3.8, whitenoise 6.9.0, psycopg2-binary 2.9.10.

## Routes confirmed
`/`, `/about/`, `/projects/`, `/projects/<slug>/`, `/language/`, `/newsletter/subscribe/`, `/favicon.ico`, `/robots.txt`, `/sitemap.xml`, admin at configured nonstandard path, and media routes.

## Limits
No explicit standalone REST API was found in URL configuration. This does not prove absence of integrations elsewhere. No test suite was found by filename inspection; this is not proof tests never existed.
