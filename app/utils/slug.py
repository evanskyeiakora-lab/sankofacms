from slugify import slugify


def generate_unique_slug(model, title, current_id=None):
    """
    Generate a unique slug.

    If current_id is supplied, ignore that record.
    Useful when editing an existing record.
    """

    base_slug = slugify(title)
    slug = base_slug
    counter = 1

    while True:

        existing = model.query.filter_by(slug=slug).first()

        if existing is None:
            break

        if current_id and existing.id == current_id:
            break

        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug