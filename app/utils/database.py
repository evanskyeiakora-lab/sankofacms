from app.extensions import db


def save(model):
    """Save a new model instance."""
    db.session.add(model)
    db.session.commit()


def commit():
    """Commit changes to an existing model."""
    db.session.commit()


def delete(model):
    """Delete a model instance."""
    db.session.delete(model)
    db.session.commit()


def rollback():
    """Rollback the current transaction."""
    db.session.rollback()