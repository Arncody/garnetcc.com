"""Recognize legacy internal links without rewriting external destinations."""

from urllib.parse import unquote, urlsplit


def _local_target(url, site_host):
    try:
        target = urlsplit((url or "").strip())
        local = urlsplit(f"//{site_host}").hostname
    except ValueError:
        return None
    if target.netloc and (target.hostname or "").removeprefix("www.") != (local or "").removeprefix("www."):
        return None
    return target


def is_retired_blog_link(url, site_host):
    target = _local_target(url, site_host)
    if target is None:
        return False
    path = unquote(target.path).strip("/")
    return path == "blog" or path.startswith("blog/") or (not path and target.fragment == "blog")


def is_legacy_about_link(url, site_host, home_path):
    target = _local_target(url, site_host)
    return (
        target is not None
        and target.path.rstrip("/") in {"", home_path.rstrip("/")}
        and target.fragment in {"about", "about-garnet"}
    )
