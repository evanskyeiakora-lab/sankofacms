# ==========================================================
# app/admin/routes.py
# Apex Citizens of Ghana
# Tenant-Aware Administration
# ==========================================================

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
)

from flask_login import current_user

from sqlalchemy import or_

from app.extensions import db

from app.admin import admin_bp

from app.models import (
    User,
    News,
    Gallery,
    Member,
    ContactMessage,
    HeroSlide,
    Page,
    Event,
    MembershipApplication,
)

from app.tenant import get_current_client

from app.utils.permissions import roles_required


# ==========================================================
# ADMIN ROLES
# ==========================================================

ADMIN_ROLES = (
    "Super Admin",
    "Administrator",
)


# ==========================================================
# CURRENT ADMIN CLIENT
# ==========================================================

def get_admin_client():
    return get_current_client()


# ==========================================================
# REQUIRE ADMIN CLIENT
# ==========================================================

def require_admin_client():

    client = get_admin_client()

    # ------------------------------------------------------
    # Super Admin can operate without a tenant
    # ------------------------------------------------------

    if client is None and current_user.is_super_admin:
        return None

    # ------------------------------------------------------
    # Normal administrators require a tenant
    # ------------------------------------------------------

    if client is None:

        flash(
            "Client could not be identified.",
            "danger",
        )

        return redirect(
            url_for("auth.login")
        )

    return client


# ==========================================================
# GET MEMBERSHIP APPLICATION
# ==========================================================

def get_membership_application(
    application_id,
    client=None,
):

    query = (
        MembershipApplication.query
        .filter(
            MembershipApplication.id == application_id
        )
    )

    # ------------------------------------------------------
    # Tenant security
    # ------------------------------------------------------

    if client is not None:

        query = query.filter(
            MembershipApplication.client_id == client.id
        )

    return query.first_or_404()


# ==========================================================
# ADMIN DASHBOARD
# ==========================================================

@admin_bp.route("/")
@roles_required(*ADMIN_ROLES)
def dashboard():

    client = require_admin_client()

    # ------------------------------------------------------
    # Redirect when client cannot be resolved
    # ------------------------------------------------------

    if (
        client is None
        and not current_user.is_super_admin
    ):

        return client

    # ======================================================
    # BASE QUERIES
    # ======================================================

    if client is not None:

        client_id = client.id

        news_query = News.query.filter(
            News.client_id == client_id
        )

        gallery_query = Gallery.query.filter(
            Gallery.client_id == client_id
        )

        member_query = Member.query.filter(
            Member.client_id == client_id
        )

        hero_query = HeroSlide.query.filter(
            HeroSlide.client_id == client_id
        )

        page_query = Page.query.filter(
            Page.client_id == client_id
        )

        event_query = Event.query.filter(
            Event.client_id == client_id
        )

        application_query = MembershipApplication.query.filter(
            MembershipApplication.client_id == client_id
        )

        user_query = User.query.filter(
            User.client_id == client_id
        )

    else:

        # --------------------------------------------------
        # Platform-level Super Admin
        # --------------------------------------------------

        news_query = News.query

        gallery_query = Gallery.query

        member_query = Member.query

        hero_query = HeroSlide.query

        page_query = Page.query

        event_query = Event.query

        application_query = MembershipApplication.query

        user_query = User.query

    # ======================================================
    # DASHBOARD STATISTICS
    # ======================================================

    stats = {

        # --------------------------------------------------
        # NEWS
        # --------------------------------------------------

        "news": news_query.count(),

        "published_news": (
            news_query
            .filter(
                News.is_published.is_(True)
            )
            .count()
        ),

        "draft_news": (
            news_query
            .filter(
                News.is_published.is_(False)
            )
            .count()
        ),

        # --------------------------------------------------
        # HERO SLIDES
        # --------------------------------------------------

        "hero": hero_query.count(),

        # --------------------------------------------------
        # EVENTS
        # --------------------------------------------------

        "events": event_query.count(),

        # --------------------------------------------------
        # PAGES
        # --------------------------------------------------

        "pages": page_query.count(),

        # --------------------------------------------------
        # GALLERY
        # --------------------------------------------------

        "gallery": gallery_query.count(),

        # --------------------------------------------------
        # MEMBERS
        # --------------------------------------------------

        "members": member_query.count(),

        # --------------------------------------------------
        # USERS
        # --------------------------------------------------

        "users": user_query.count(),

        # --------------------------------------------------
        # CONTACT MESSAGES
        #
        # ContactMessage currently has no client_id.
        # This will be made tenant-aware later.
        # --------------------------------------------------

        "messages": ContactMessage.query.count(),

        # --------------------------------------------------
        # MEMBERSHIP APPLICATIONS
        # --------------------------------------------------

        "applications": application_query.count(),

        "membership_applications": application_query.count(),

        "approved_applications": (
            application_query
            .filter(
                MembershipApplication.status == "Approved"
            )
            .count()
        ),

        "pending_applications": (
            application_query
            .filter(
                MembershipApplication.status == "Pending"
            )
            .count()
        ),

        "rejected_applications": (
            application_query
            .filter(
                MembershipApplication.status == "Rejected"
            )
            .count()
        ),
    }

    # ======================================================
    # RECENT NEWS
    # ======================================================

    recent_news = (
        news_query
        .order_by(
            News.created_at.desc()
        )
        .limit(5)
        .all()
    )

    # ======================================================
    # RECENT EVENTS
    # ======================================================

    recent_events = (
        event_query
        .order_by(
            Event.created_at.desc()
        )
        .limit(5)
        .all()
    )

    # ======================================================
    # RECENT MEMBERS
    # ======================================================

    recent_members = (
        member_query
        .order_by(
            Member.created_at.desc()
        )
        .limit(5)
        .all()
    )

    # ======================================================
    # RECENT GALLERY
    # ======================================================

    recent_gallery = (
        gallery_query
        .order_by(
            Gallery.created_at.desc()
        )
        .limit(5)
        .all()
    )

    # ======================================================
    # RECENT HERO SLIDES
    # ======================================================

    recent_slides = (
        hero_query
        .order_by(
            HeroSlide.display_order.asc(),
            HeroSlide.id.asc(),
        )
        .limit(5)
        .all()
    )

    # ======================================================
    # RECENT MEMBERSHIP APPLICATIONS
    # ======================================================

    recent_applications = (
        application_query
        .order_by(
            MembershipApplication.created_at.desc()
        )
        .limit(5)
        .all()
    )

    # ======================================================
    # RECENT CONTACT MESSAGES
    # ======================================================

    recent_messages = (
        ContactMessage.query
        .order_by(
            ContactMessage.created_at.desc()
        )
        .limit(5)
        .all()
    )

    # ======================================================
    # RENDER DASHBOARD
    # ======================================================

    return render_template(
        "admin/dashboard.html",

        client=client,

        stats=stats,

        recent_news=recent_news,

        recent_events=recent_events,

        recent_messages=recent_messages,

        recent_members=recent_members,

        recent_gallery=recent_gallery,

        recent_slides=recent_slides,

        recent_applications=recent_applications,
    )


# ==========================================================
# MEMBERSHIP APPLICATIONS
# ==========================================================

@admin_bp.route(
    "/membership-applications"
)
@roles_required(*ADMIN_ROLES)
def membership_applications():

    client = require_admin_client()

    if (
        client is None
        and not current_user.is_super_admin
    ):

        return client

    # ======================================================
    # PAGE
    # ======================================================

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    if page < 1:
        page = 1

    # ======================================================
    # SEARCH
    # ======================================================

    search = request.args.get(
        "search",
        "",
        type=str,
    ).strip()

    # ======================================================
    # STATUS
    # ======================================================

    status = request.args.get(
        "status",
        "",
        type=str,
    ).strip()

    # ======================================================
    # BASE QUERY
    # ======================================================

    query = MembershipApplication.query

    # ======================================================
    # TENANT FILTER
    # ======================================================

    if client is not None:

        query = query.filter(
            MembershipApplication.client_id == client.id
        )

    # ======================================================
    # SEARCH FILTER
    # ======================================================

    if search:

        search_term = f"%{search}%"

        query = query.filter(
            or_(
                MembershipApplication.full_name.ilike(
                    search_term
                ),

                MembershipApplication.email.ilike(
                    search_term
                ),

                MembershipApplication.phone.ilike(
                    search_term
                ),

                MembershipApplication.location.ilike(
                    search_term
                ),
            )
        )

    # ======================================================
    # STATUS FILTER
    # ======================================================

    allowed_statuses = (
        "Pending",
        "Approved",
        "Rejected",
    )

    if status in allowed_statuses:

        query = query.filter(
            MembershipApplication.status == status
        )

    # ======================================================
    # PAGINATION
    # ======================================================

    applications = (
        query
        .order_by(
            MembershipApplication.created_at.desc()
        )
        .paginate(
            page=page,
            per_page=10,
            error_out=False,
        )
    )

    # ======================================================
    # COUNTERS
    # ======================================================

    counter_query = MembershipApplication.query

    if client is not None:

        counter_query = counter_query.filter(
            MembershipApplication.client_id == client.id
        )

    total_applications = counter_query.count()

    pending_applications = (
        counter_query
        .filter(
            MembershipApplication.status == "Pending"
        )
        .count()
    )

    approved_applications = (
        counter_query
        .filter(
            MembershipApplication.status == "Approved"
        )
        .count()
    )

    rejected_applications = (
        counter_query
        .filter(
            MembershipApplication.status == "Rejected"
        )
        .count()
    )

    # ======================================================
    # RENDER
    # ======================================================

    return render_template(
        "admin/membership_applications/index.html",

        client=client,

        applications=applications,

        search=search,

        status=status,

        total_applications=total_applications,

        pending_applications=pending_applications,

        approved_applications=approved_applications,

        rejected_applications=rejected_applications,
    )


# ==========================================================
# VIEW MEMBERSHIP APPLICATION
# ==========================================================

@admin_bp.route(
    "/membership-applications/<int:id>"
)
@roles_required(*ADMIN_ROLES)
def view_membership_application(id):

    client = require_admin_client()

    if (
        client is None
        and not current_user.is_super_admin
    ):

        return client

    application = get_membership_application(
        application_id=id,
        client=client,
    )

    return render_template(
        "admin/membership_applications/view.html",

        client=client,

        application=application,
    )


# ==========================================================
# UPDATE APPLICATION STATUS
# ==========================================================

@admin_bp.route(
    "/membership-applications/<int:id>/status/<string:status>",
    methods=["POST"],
)
@roles_required(*ADMIN_ROLES)
def update_membership_application_status(
    id,
    status,
):

    client = require_admin_client()

    if (
        client is None
        and not current_user.is_super_admin
    ):

        return client

    # ======================================================
    # ALLOWED STATUSES
    # ======================================================

    allowed_statuses = (
        "Pending",
        "Approved",
        "Rejected",
    )

    if status not in allowed_statuses:

        flash(
            "Invalid application status.",
            "danger",
        )

        return redirect(
            url_for(
                "admin.membership_applications"
            )
        )

    # ======================================================
    # GET APPLICATION
    # ======================================================

    application = get_membership_application(
        application_id=id,
        client=client,
    )

    # ======================================================
    # PREVENT STATUS CHANGE AFTER CONVERSION
    # ======================================================

    if application.is_converted:

        flash(
            "A converted application cannot have its status changed.",
            "warning",
        )

        return redirect(
            url_for(
                "admin.view_membership_application",
                id=application.id,
            )
        )

    # ======================================================
    # UPDATE
    # ======================================================

    application.status = status

    try:

        db.session.commit()

    except Exception as e:

        db.session.rollback()

        print(
            "APPLICATION STATUS ERROR:",
            type(e).__name__,
            str(e),
        )

        flash(
            "The application status could not be updated.",
            "danger",
        )

        return redirect(
            url_for(
                "admin.view_membership_application",
                id=application.id,
            )
        )

    flash(
        f"Application status changed to {status}.",
        "success",
    )

    return redirect(
        url_for(
            "admin.view_membership_application",
            id=application.id,
        )
    )


# ==========================================================
# CONVERT APPLICATION TO MEMBER
# ==========================================================

@admin_bp.route(
    "/membership-applications/<int:id>/convert",
    methods=["POST"],
)
@roles_required(*ADMIN_ROLES)
def convert_membership_application(id):

    client = require_admin_client()

    if (
        client is None
        and not current_user.is_super_admin
    ):

        return client

    # ======================================================
    # GET APPLICATION
    # ======================================================

    application = get_membership_application(
        application_id=id,
        client=client,
    )

    # ======================================================
    # PREVENT DUPLICATE CONVERSION
    # ======================================================

    if application.is_converted:

        flash(
            "This application has already been converted to a member.",
            "warning",
        )

        return redirect(
            url_for(
                "admin.view_membership_application",
                id=application.id,
            )
        )

    # ======================================================
    # ONLY APPROVED APPLICATIONS
    # ======================================================

    if application.status != "Approved":

        flash(
            "Only an approved application can be converted to a member.",
            "warning",
        )

        return redirect(
            url_for(
                "admin.view_membership_application",
                id=application.id,
            )
        )

    # ======================================================
    # CREATE MEMBER
    # ======================================================

    try:

        member = Member(
            client_id=application.client_id,

            full_name=application.full_name,

            position="Member",

            biography=None,

            email=application.email,

            phone=application.phone,

            is_active=True,
        )

        db.session.add(member)

        # --------------------------------------------------
        # Generate new member ID
        # --------------------------------------------------

        db.session.flush()

        # --------------------------------------------------
        # Update application
        # --------------------------------------------------

        application.is_converted = True

        application.member_id = member.id

        application.status = "Approved"

        # --------------------------------------------------
        # Save
        # --------------------------------------------------

        db.session.commit()

    except Exception as e:

        db.session.rollback()

        # --------------------------------------------------
        # Print REAL ERROR to Flask terminal
        # --------------------------------------------------

        print("\n" + "=" * 70)
        print("MEMBERSHIP CONVERSION ERROR")
        print("=" * 70)
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", str(e))
        print("=" * 70 + "\n")

        flash(
            f"Conversion failed: {str(e)}",
            "danger",
        )

        return redirect(
            url_for(
                "admin.view_membership_application",
                id=application.id,
            )
        )

    # ======================================================
    # SUCCESS
    # ======================================================

    flash(
        "Membership application successfully converted to a member.",
        "success",
    )

    return redirect(
        url_for(
            "admin.view_membership_application",
            id=application.id,
        )
    )


# ==========================================================
# DELETE MEMBERSHIP APPLICATION
# ==========================================================

@admin_bp.route(
    "/membership-applications/<int:id>/delete",
    methods=["POST"],
)
@roles_required(*ADMIN_ROLES)
def delete_membership_application(id):

    client = require_admin_client()

    if (
        client is None
        and not current_user.is_super_admin
    ):

        return client

    # ======================================================
    # GET APPLICATION
    # ======================================================

    application = get_membership_application(
        application_id=id,
        client=client,
    )

    # ======================================================
    # PROTECT CONVERTED APPLICATION
    # ======================================================

    if application.is_converted:

        flash(
            "A converted membership application cannot be deleted.",
            "warning",
        )

        return redirect(
            url_for(
                "admin.view_membership_application",
                id=application.id,
            )
        )

    # ======================================================
    # DELETE
    # ======================================================

    try:

        db.session.delete(application)

        db.session.commit()

    except Exception as e:

        db.session.rollback()

        print(
            "APPLICATION DELETE ERROR:",
            type(e).__name__,
            str(e),
        )

        flash(
            "The membership application could not be deleted.",
            "danger",
        )

        return redirect(
            url_for(
                "admin.view_membership_application",
                id=application.id,
            )
        )

    # ======================================================
    # SUCCESS
    # ======================================================

    flash(
        "Membership application deleted successfully.",
        "success",
    )

    return redirect(
        url_for(
            "admin.membership_applications"
        )
    )