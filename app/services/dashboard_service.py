from app.models import (
    News,
    Event,
    Hero,
    Gallery,
    Member,
    Page,
    User,
)


class DashboardService:
    """
    Service responsible for providing data
    used by the admin dashboard.
    """

    @staticmethod
    def statistics():
        """
        Return the main dashboard statistics.
        """

        return {
            "news": News.query.count(),
            "events": Event.query.count(),
            "hero": Hero.query.count(),
            "gallery": Gallery.query.count(),
            "members": Member.query.count(),
            "pages": Page.query.count(),
            "users": User.query.count(),
        }

    @staticmethod
    def recent_news(limit=5):
        """
        Return the most recent news articles.
        """

        return (
            News.query
            .order_by(News.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def recent_events(limit=5):
        """
        Return the most recent events.
        """

        return (
            Event.query
            .order_by(Event.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def recent_members(limit=5):
        """
        Return the most recently registered members.
        """

        return (
            Member.query
            .order_by(Member.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def system_info():
        """
        Basic Apex CMS system information.
        """

        return {
            "cms_version": "1.0",
            "framework": "Flask",
            "database": "SQLite",
        }