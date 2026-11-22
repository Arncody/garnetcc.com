"""Detect older menu entries that still point to the retired blog."""

from urllib.parse import unquote, urlsplit


def is_retired_blog_link(url, site_host):
    try:
        target = urlsplit((url or "").strip())
        local = urlsplit(f"//{site_host}").hostname
    except ValueError:
        return False
    if target.netloc and (target.hostname or "").removeprefix("www.") != (local or "").removeprefix("www."):
        return False
    path = unquote(target.path).strip("/")
    return path == "blog" or path.startswith("blog/") or (not path and target.fragment == "blog")
