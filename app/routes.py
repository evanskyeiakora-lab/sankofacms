# ==========================================================
# app/routes.py
# Apex Citizens of Ghana
# Tenant-Aware Public Website Routes
# ==========================================================

from datetime import date

from flask import (
    render_template,
    request,
    abort
)

from . import main_bp

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


# ==========================================================
# CURRENT CLIENT
# ==========================================================

def current_client_or_404():
    """
    Resolve the current website client from the
    incoming domain.
    """

    client = get_current_client()

    if not client:
        abort(404)

    return client


# ==========================================================
# HOME
# ==========================================================

@main_bp.route("/")
def home():

    # ------------------------------------------------------
    # CURRENT CLIENT
    # ------------------------------------------------------

    client = current_client_or_404()


    # ------------------------------------------------------
    # HERO SLIDES
    # ------------------------------------------------------

    slides = (
        HeroSlide.query
        .filter(
            HeroSlide.client_id == client.id,
            HeroSlide.is_active.is_(True)
        )
        .order_by(
            HeroSlide.display_order.asc(),
            HeroSlide.id.asc()
        )
        .all()
    )


    # ------------------------------------------------------
    # ABOUT PAGE
    # ------------------------------------------------------

    about_page = (
        Page.query
        .filter(
            Page.client_id == client.id,
            Page.page_role == "about-us",
            Page.is_published.is_(True)
        )
        .first()
    )


    # ------------------------------------------------------
    # VISION PAGE
    # ------------------------------------------------------

    vision_page = (
        Page.query
        .filter(
            Page.client_id == client.id,
            Page.page_role == "vision",
            Page.is_published.is_(True)
        )
        .first()
    )


    # ------------------------------------------------------
    # MISSION PAGE
    # ------------------------------------------------------

    mission_page = (
        Page.query
        .filter(
            Page.client_id == client.id,
            Page.page_role == "mission",
            Page.is_published.is_(True)
        )
        .first()
    )


    # ------------------------------------------------------
    # HISTORY PAGE
    # ------------------------------------------------------

    history_page = (
        Page.query
        .filter(
            Page.client_id == client.id,
            Page.page_role == "history",
            Page.is_published.is_(True)
        )
        .first()
    )


    # ------------------------------------------------------
    # LATEST NEWS
    # ------------------------------------------------------

    latest_news = (
        News.query
        .filter(
            News.client_id == client.id,
            News.is_published.is_(True)
        )
        .order_by(
            News.published_at.desc(),
            News.id.desc()
        )
        .limit(3)
        .all()
    )


    # ------------------------------------------------------
    # UPCOMING EVENTS
    # ------------------------------------------------------

    upcoming_events = (
        Event.query
        .filter(
            Event.client_id == client.id,
            Event.is_published.is_(True),
            Event.start_date >= date.today()
        )
        .order_by(
            Event.start_date.asc(),
            Event.start_time.asc(),
            Event.display_order.asc()
        )
        .limit(3)
        .all()
    )


    # ------------------------------------------------------
    # FEATURED GALLERY
    # ------------------------------------------------------

    featured_gallery = (
        Gallery.query
        .filter(
            Gallery.client_id == client.id,
            Gallery.is_published.is_(True),
            Gallery.is_featured.is_(True)
        )
        .order_by(
            Gallery.display_order.asc(),
            Gallery.created_at.desc()
        )
        .limit(8)
        .all()
    )


    # ------------------------------------------------------
    # LEADERSHIP
    # ------------------------------------------------------

    leaders = (
        Leader.query
        .filter(
            Leader.client_id == client.id,
            Leader.is_active.is_(True)
        )
        .order_by(
            Leader.display_order.asc(),
            Leader.name.asc()
        )
        .limit(8)
        .all()
    )


    # ------------------------------------------------------
    # WEBSITE STATISTICS
    # ------------------------------------------------------

    stats = {

        "members_count": (
            Member.query
            .filter(
                Member.client_id == client.id
            )
            .count()
        ),

        "leaders_count": (
            Leader.query
            .filter(
                Leader.client_id == client.id,
                Leader.is_active.is_(True)
            )
            .count()
        ),

        "news_count": (
            News.query
            .filter(
                News.client_id == client.id,
                News.is_published.is_(True)
            )
            .count()
        ),

        "events_count": (
            Event.query
            .filter(
                Event.client_id == client.id,
                Event.is_published.is_(True)
            )
            .count()
        ),

        "gallery_count": (
            Gallery.query
            .filter(
                Gallery.client_id == client.id,
                Gallery.is_published.is_(True)
            )
            .count()
        )
    }


    # ------------------------------------------------------
    # RENDER HOMEPAGE
    # ------------------------------------------------------

    return render_template(
        "index.html",

        client=client,

        slides=slides,

        about_page=about_page,

        vision_page=vision_page,

        mission_page=mission_page,

        history_page=history_page,

        latest_news=latest_news,

        upcoming_events=upcoming_events,

        featured_gallery=featured_gallery,

        leaders=leaders,

        stats=stats
    )


# ==========================================================
# DYNAMIC WEBSITE PAGES
# ==========================================================

@main_bp.route(
    "/page/<slug>/"
)
def page(slug):

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
        "page.html",
        client=client,
        page=website_page
    )