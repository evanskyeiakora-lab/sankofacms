
from datetime import date
from xml.sax.saxutils import escape

from flask import (
    render_template,
    redirect,
    url_for,
    request,
    Response,
    abort,
    current_app
)

from . import main_bp

from app.extensions import db
from app.models import (
    News,
    HeroSlide,
    Page,
    Event,
    Gallery,
    Leader,
    Member
)

from app.tenant import get_current_client


# ============================================================
# TENANT HELPER
# ============================================================

def current_client_or_404():
    """
    Get the current client based on the request domain.

    Returns:
        Client object

    Raises:
        404 if no active client is found.
    """

    client = get_current_client()

    if not client:
        abort(
            404,
            description="Website client not found."
        )

    return client



# ============================================================
# HOMEPAGE
# ============================================================

@main_bp.route("/")
def home():
    """
    Public homepage.
    """

    client = current_client_or_404()

    # ========================================================
    # HERO SLIDES
    # ========================================================

    hero_slides = (
        HeroSlide.query
        .filter(
            HeroSlide.client_id == client.id,
            HeroSlide.is_active.is_(True)
        )
        .order_by(
            HeroSlide.display_order.asc()
        )
        .all()
    )

    # ========================================================
    # LATEST NEWS
    # ========================================================

    latest_news = (
        News.query
        .filter(
            News.client_id == client.id,
            News.is_published.is_(True)
        )
        .order_by(
            News.created_at.desc()
        )
        .limit(6)
        .all()
    )

    # ========================================================
    # UPCOMING EVENTS
    # ========================================================

    upcoming_events = (
        Event.query
        .filter(
            Event.client_id == client.id,
            Event.is_published.is_(True),
            Event.start_date >= date.today()
        )
        .order_by(
            Event.start_date.asc()
        )
        .limit(6)
        .all()
    )

    # ========================================================
    # GALLERY ITEMS
    # ========================================================

    gallery_items = (
        Gallery.query
        .filter(
            Gallery.client_id == client.id,
            Gallery.is_published.is_(True)
        )
        .order_by(
            Gallery.created_at.desc()
        )
        .limit(6)
        .all()
    )

    # ========================================================
    # LEADERS
    # ========================================================

    leaders = (
        Leader.query
        .filter(
            Leader.client_id == client.id,
            Leader.is_active.is_(True)
        )
        .order_by(
            Leader.display_order.asc()
        )
        .limit(6)
        .all()
    )

    # ========================================================
    # WEBSITE STATISTICS
    # ========================================================

    news_count = (
        News.query
        .filter(
            News.client_id == client.id,
            News.is_published.is_(True)
        )
        .count()
    )

    events_count = (
        Event.query
        .filter(
            Event.client_id == client.id,
            Event.is_published.is_(True)
        )
        .count()
    )

    members_count = (
        Member.query
        .filter(
            Member.client_id == client.id
        )
        .count()
    )

    gallery_count = (
        Gallery.query
        .filter(
            Gallery.client_id == client.id,
            Gallery.is_published.is_(True)
        )
        .count()
    )

    stats = {
        "news_count": news_count,
        "events_count": events_count,
        "members_count": members_count,
        "gallery_count": gallery_count
    }

    # ========================================================
    # RENDER HOMEPAGE
    # ========================================================

    return render_template(
        "home/index.html",
        client=client,
        hero_slides=hero_slides,
        latest_news=latest_news,
        upcoming_events=upcoming_events,
        gallery_items=gallery_items,
        leaders=leaders,
        stats=stats
    )


    # ========================================================
    # WEBSITE STATISTICS
    # ========================================================

    news_count = (
        News.query
        .filter(
            News.client_id == client.id,
            News.is_published.is_(True)
        )
        .count()
    )

    events_count = (
        Event.query
        .filter(
            Event.client_id == client.id,
            Event.is_published.is_(True)
        )
        .count()
    )

    stats = {
        "news_count": news_count,
        "events_count": events_count
    }



# ============================================================
# DYNAMIC WEBSITE PAGES
# ============================================================

@main_bp.route("/page/<slug>/")
def page(slug):
    """
    Display a published dynamic website page.
    """

    client = current_client_or_404()

    website_page = (
        Page.query
        .filter(
            Page.client_id == client.id,
            Page.slug == slug,
            Page.is_published.is_(True)
        )
        .first_or_404()
    )

    return render_template(
        "public/page.html",
        page=website_page,
        client=client
    )


# ============================================================
# ABOUT PAGE
# ============================================================

@main_bp.route("/about/")
def about():
    """
    Display the About page.
    """

    client = current_client_or_404()

    website_page = (
        Page.query
        .filter(
            Page.client_id == client.id,
            Page.slug == "about",
            Page.is_published.is_(True)
        )
        .first()
    )

    if website_page:
        return render_template(
            "public/page.html",
            page=website_page,
            client=client
        )

    return render_template(
        "public/about.html",
        client=client
    )


# ============================================================
# ROBOTS.TXT
# ============================================================

@main_bp.route("/robots.txt")
def robots():
    """
    Generate a dynamic robots.txt file.
    """

    current_client_or_404()

    sitemap_url = url_for(
        "main.sitemap",
        _external=True
    )

    robots_content = f"""User-agent: *
Allow: /

Disallow: /admin/
Disallow: /auth/

Sitemap: {sitemap_url}
"""

    return Response(
        robots_content,
        mimetype="text/plain"
    )


# ============================================================
# XML SITEMAP
# ============================================================

@main_bp.route("/sitemap.xml")
def sitemap():
    """
    Generate a dynamic XML sitemap for the current client.
    """

    client = current_client_or_404()

    urls = []

    def add_url(endpoint, **values):
        """
        Safely generate a URL and add it to the sitemap.
        """

        try:
            page_url = url_for(
                endpoint,
                _external=True,
                **values
            )

            urls.append(page_url)

        except Exception:
            current_app.logger.warning(
                "Could not generate sitemap URL: %s",
                endpoint,
                exc_info=True
            )

    # --------------------------------------------------------
    # STATIC WEBSITE URLS
    # --------------------------------------------------------

    static_endpoints = [
        "main.home",
        "main.about",
        "main.news",
        "main.events",
        "main.gallery",
        "main.leadership",
        "main.members",
        "main.join_us"
    ]

    for endpoint in static_endpoints:
        add_url(endpoint)

    # --------------------------------------------------------
    # DYNAMIC WEBSITE PAGES
    # --------------------------------------------------------

    website_pages = (
        Page.query
        .filter(
            Page.client_id == client.id,
            Page.is_published.is_(True)
        )
        .all()
    )

    for website_page in website_pages:
        if website_page.slug:
            add_url(
                "main.page",
                slug=website_page.slug
            )

    # --------------------------------------------------------
    # PUBLISHED NEWS ARTICLES
    # --------------------------------------------------------

    news_articles = (
        News.query
        .filter(
            News.client_id == client.id,
            News.is_published.is_(True)
        )
        .all()
    )

    for article in news_articles:
        if article.slug:
            add_url(
                "main.news_detail",
                slug=article.slug
            )

    # --------------------------------------------------------
    # PUBLISHED EVENTS
    # --------------------------------------------------------

    published_events = (
        Event.query
        .filter(
            Event.client_id == client.id,
            Event.is_published.is_(True)
        )
        .all()
    )

    for event in published_events:
        if event.slug:
            add_url(
                "main.event_detail",
                slug=event.slug
            )

    # --------------------------------------------------------
    # PUBLISHED GALLERY ITEMS
    # --------------------------------------------------------

    gallery_items = (
        Gallery.query
        .filter(
            Gallery.client_id == client.id,
            Gallery.is_published.is_(True)
        )
        .all()
    )

    for gallery_item in gallery_items:
        if gallery_item.slug:
            add_url(
                "main.gallery_detail",
                slug=gallery_item.slug
            )

    # --------------------------------------------------------
    # REMOVE DUPLICATE URLS
    # --------------------------------------------------------

    urls = list(dict.fromkeys(urls))

    # --------------------------------------------------------
    # BUILD XML CONTENT
    # --------------------------------------------------------

    sitemap_entries = []

    for page_url in urls:
        safe_url = escape(page_url)

        sitemap_entries.append(
            "    <url>\n"
            f"        <loc>{safe_url}</loc>\n"
            "    </url>"
        )

    sitemap_content = "\n".join(
        sitemap_entries
    )

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_content}
</urlset>
"""

    return Response(
        xml,
        mimetype="application/xml"
    )


# ============================================================
# NEWS
# ============================================================

@main_bp.route("/news/")
def news():
    """
    Display published news articles.
    """

    client = current_client_or_404()

    news_articles = (
        News.query
        .filter(
            News.client_id == client.id,
            News.is_published.is_(True)
        )
        .order_by(
            News.created_at.desc()
        )
        .all()
    )

    return render_template(
        "public/news/index.html",
        news_articles=news_articles,
        client=client
    )


@main_bp.route("/news/<slug>/")
def news_detail(slug):
    """
    Display a single published news article.
    """

    client = current_client_or_404()

    article = (
        News.query
        .filter(
            News.client_id == client.id,
            News.slug == slug,
            News.is_published.is_(True)
        )
        .first_or_404()
    )

    return render_template(
        "public/news/detail.html",
        article=article,
        client=client
    )


# ============================================================
# EVENTS
# ============================================================

@main_bp.route("/events/")
def events():
    """
    Display published events.
    """

    client = current_client_or_404()

    published_events = (
        Event.query
        .filter(
            Event.client_id == client.id,
            Event.is_published.is_(True)
        )
        .order_by(
            Event.start_date.asc()
        )
        .all()
    )

    return render_template(
        "public/events/index.html",
        events=published_events,
        client=client
    )


@main_bp.route("/events/<slug>/")
def event_detail(slug):
    """
    Display a single published event.
    """

    client = current_client_or_404()

    event = (
        Event.query
        .filter(
            Event.client_id == client.id,
            Event.slug == slug,
            Event.is_published.is_(True)
        )
        .first_or_404()
    )

    return render_template(
        "public/events/detail.html",
        event=event,
        client=client
    )


# ============================================================
# GALLERY
# ============================================================

@main_bp.route("/gallery/")
def gallery():
    """
    Display published gallery items.
    """

    client = current_client_or_404()

    gallery_items = (
        Gallery.query
        .filter(
            Gallery.client_id == client.id,
            Gallery.is_published.is_(True)
        )
        .order_by(
            Gallery.created_at.desc()
        )
        .all()
    )

    return render_template(
        "public/gallery/index.html",
        gallery_items=gallery_items,
        client=client
    )


@main_bp.route("/gallery/<slug>/")
def gallery_detail(slug):
    """
    Display a single published gallery item.
    """

    client = current_client_or_404()

    gallery_item = (
        Gallery.query
        .filter(
            Gallery.client_id == client.id,
            Gallery.slug == slug,
            Gallery.is_published.is_(True)
        )
        .first_or_404()
    )

    return render_template(
        "public/gallery/detail.html",
        gallery_item=gallery_item,
        client=client
    )


# ============================================================
# LEADERSHIP
# ============================================================

@main_bp.route("/leadership/")
def leadership():
    """
    Display active organizational leaders.
    """

    client = current_client_or_404()

    leaders = (
        Leader.query
        .filter(
            Leader.client_id == client.id,
            Leader.is_active.is_(True)
        )
        .order_by(
            Leader.display_order.asc()
        )
        .all()
    )

    return render_template(
        "public/leadership.html",
        leaders=leaders,
        client=client
    )


# ============================================================
# MEMBERS
# ============================================================

@main_bp.route("/members/")
def members():
    """
    Display active members.
    """

    client = current_client_or_404()

    active_members = (
        Member.query
        .filter(
            Member.client_id == client.id,
            Member.is_active.is_(True)
        )
        .order_by(
            Member.created_at.desc()
        )
        .all()
    )

    return render_template(
        "public/members/index.html",
        members=active_members,
        client=client
    )


@main_bp.route("/members/<int:id>/")
def member_detail(id):
    """
    Display an individual active member.
    """

    client = current_client_or_404()

    member = (
        Member.query
        .filter(
            Member.id == id,
            Member.client_id == client.id,
            Member.is_active.is_(True)
        )
        .first_or_404()
    )

    return render_template(
        "public/members/detail.html",
        member=member,
        client=client
    )


# ============================================================
# JOIN US
# ============================================================

@main_bp.route("/join-us/")
def join_us():
    """
    Display the membership registration page.
    """

    client = current_client_or_404()

    return render_template(
        "public/join_us.html",
        client=client
    )


# ============================================================
# TENANT TEST ROUTE
# ============================================================

@main_bp.route("/test-client/")
def test_client():
    """
    Test the current tenant/client resolution.
    """

    client = current_client_or_404()

    return {
        "id": client.id,
        "name": client.name,
        "domain": client.domain,
        "is_active": client.is_active
    }