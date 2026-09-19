# ==========================================================
# app/members/routes.py
# Apex Citizens of Ghana
# Tenant-Aware Admin Member Management
# ==========================================================

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
)

from . import members_bp

from .forms import (
    MemberForm,
    DeleteMemberForm,
)

from app.extensions import db
from app.models import Member
from app.tenant import get_current_client

from app.utils.file_upload import (
    save_image,
    delete_image,
)

from app.utils.permissions import roles_required


# ==========================================================
# ALLOWED ROLES
# ==========================================================

MEMBER_ROLES = (
    "Super Admin",
    "Administrator",
    "Editor",
)


# ==========================================================
# MEMBERS LIST
# ==========================================================

@members_bp.route("/")
@roles_required(*MEMBER_ROLES)
def index():

    client = get_current_client()

    if not client:
        flash(
            "Client could not be identified.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    search = request.args.get(
        "search",
        "",
    ).strip()

    delete_form = DeleteMemberForm()

    query = (
        Member.query
        .filter(
            Member.client_id == client.id
        )
    )

    if search:

        query = query.filter(
            Member.full_name.ilike(
                f"%{search}%"
            )
        )

    members = (
        query
        .order_by(
            Member.display_order.asc(),
            Member.full_name.asc(),
        )
        .paginate(
            page=page,
            per_page=10,
            error_out=False,
        )
    )

    return render_template(
        "admin/members/index.html",
        client=client,
        members=members,
        search=search,
        delete_form=delete_form,
    )


# ==========================================================
# CREATE MEMBER
# ==========================================================

@members_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@roles_required(*MEMBER_ROLES)
def create():

    client = get_current_client()

    if not client:
        flash(
            "Client could not be identified.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    form = MemberForm()

    if form.validate_on_submit():

        filename = None

        if form.photo.data:

            filename = save_image(
                form.photo.data,
                "members",
            )

        member = Member(
            client_id=client.id,
            full_name=form.full_name.data,
            position=form.position.data,
            biography=form.biography.data,
            photo=filename,
            email=form.email.data,
            phone=form.phone.data,
            facebook=form.facebook.data,
            linkedin=form.linkedin.data,
            twitter=form.twitter.data,
            display_order=form.display_order.data,
            is_active=form.is_active.data,
        )

        db.session.add(member)
        db.session.commit()

        flash(
            "Member created successfully.",
            "success",
        )

        return redirect(
            url_for("members.index")
        )

    return render_template(
        "admin/members/create.html",
        client=client,
        form=form,
    )


# ==========================================================
# EDIT MEMBER
# ==========================================================

@members_bp.route(
    "/edit/<int:id>",
    methods=["GET", "POST"],
)
@roles_required(*MEMBER_ROLES)
def edit(id):

    client = get_current_client()

    if not client:
        flash(
            "Client could not be identified.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    member = (
        Member.query
        .filter(
            Member.id == id,
            Member.client_id == client.id,
        )
        .first_or_404()
    )

    form = MemberForm(obj=member)

    if form.validate_on_submit():

        member.full_name = form.full_name.data
        member.position = form.position.data
        member.biography = form.biography.data

        member.email = form.email.data
        member.phone = form.phone.data

        member.facebook = form.facebook.data
        member.linkedin = form.linkedin.data
        member.twitter = form.twitter.data

        member.display_order = form.display_order.data
        member.is_active = form.is_active.data

        if form.photo.data:

            old_photo = member.photo

            filename = save_image(
                form.photo.data,
                "members",
            )

            if filename:

                member.photo = filename

                if old_photo:

                    delete_image(
                        old_photo,
                        "members",
                    )

        db.session.commit()

        flash(
            "Member updated successfully.",
            "success",
        )

        return redirect(
            url_for("members.index")
        )

    return render_template(
        "admin/members/edit.html",
        client=client,
        form=form,
        member=member,
    )


# ==========================================================
# DELETE MEMBER
# ==========================================================

@members_bp.route(
    "/delete/<int:id>",
    methods=["POST"],
)
@roles_required(*MEMBER_ROLES)
def delete(id):

    client = get_current_client()

    if not client:
        flash(
            "Client could not be identified.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    form = DeleteMemberForm()

    if not form.validate_on_submit():

        flash(
            "Invalid delete request.",
            "danger",
        )

        return redirect(
            url_for("members.index")
        )

    member = (
        Member.query
        .filter(
            Member.id == id,
            Member.client_id == client.id,
        )
        .first_or_404()
    )

    if member.photo:

        delete_image(
            member.photo,
            "members",
        )

    db.session.delete(member)
    db.session.commit()

    flash(
        "Member deleted successfully.",
        "success",
    )

    return redirect(
        url_for("members.index")
    )