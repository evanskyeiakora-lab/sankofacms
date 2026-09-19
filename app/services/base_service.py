from app.extensions import db


class BaseService:
    """
    Base service providing common CRUD operations.

    Child services should define:
        model = ModelClass
    """

    model = None

    # =====================================================
    # Get All
    # =====================================================

    @classmethod
    def get_all(cls):
        return cls.model.query.all()

    # =====================================================
    # Get By ID
    # =====================================================

    @classmethod
    def get_by_id(cls, object_id):
        return cls.model.query.get_or_404(object_id)

    # =====================================================
    # Get First
    # =====================================================

    @classmethod
    def get_first(cls):
        return cls.model.query.first()

    # =====================================================
    # Count
    # =====================================================

    @classmethod
    def count(cls):
        return cls.model.query.count()

    # =====================================================
    # Create
    # =====================================================

    @classmethod
    def create(cls, obj):
        try:
            db.session.add(obj)
            db.session.commit()
            return obj

        except Exception:
            db.session.rollback()
            raise

    # =====================================================
    # Save
    # =====================================================

    @classmethod
    def save(cls, obj):
        """
        Save a new or existing object.
        """

        try:
            db.session.add(obj)
            db.session.commit()
            return obj

        except Exception:
            db.session.rollback()
            raise

    # =====================================================
    # Update
    # =====================================================

    @classmethod
    def update(cls):
        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

    # =====================================================
    # Delete
    # =====================================================

    @classmethod
    def delete(cls, obj):
        try:
            db.session.delete(obj)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

    # =====================================================
    # Commit
    # =====================================================

    @classmethod
    def commit(cls):
        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

    # =====================================================
    # Rollback
    # =====================================================

    @classmethod
    def rollback(cls):
        db.session.rollback()

    # =====================================================
    # Exists
    # =====================================================

    @classmethod
    def exists(cls, **filters):
        return cls.model.query.filter_by(**filters).first() is not None

    # =====================================================
    # Find One
    # =====================================================

    @classmethod
    def find_one(cls, **filters):
        return cls.model.query.filter_by(**filters).first()

    # =====================================================
    # Find All
    # =====================================================

    @classmethod
    def find_all(cls, **filters):
        return cls.model.query.filter_by(**filters).all()

    # =====================================================
    # Paginate
    # =====================================================

    @classmethod
    def paginate(
        cls,
        page=1,
        per_page=10,
        query=None
    ):
        """
        Paginate records.

        Usage:
            UserService.paginate(page=1)

            or

            UserService.paginate(
                page=page,
                query=query
            )
        """

        if query is None:
            query = cls.model.query

        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )