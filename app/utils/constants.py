NEWS_FOLDER = "news"
EVENTS_FOLDER = "events"
HERO_FOLDER = "hero"
GALLERY_FOLDER = "gallery"
MEMBERS_FOLDER = "members"
PAGES_FOLDER = "pages"
SETTINGS_FOLDER = "settings"
USERS_FOLDER = "users"
LEADERS_FOLDER = "leaders"

ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp"
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

class Roles:
    SUPER_ADMIN = "Super Admin"
    ADMINISTRATOR = "Administrator"
    EDITOR = "Editor"
    AUTHOR = "Author"
    MODERATOR = "Moderator"

    CHOICES = [
        (SUPER_ADMIN, "Super Admin"),
        (ADMINISTRATOR, "Administrator"),
        (EDITOR, "Editor"),
        (AUTHOR, "Author"),
        (MODERATOR, "Moderator"),
    ]

