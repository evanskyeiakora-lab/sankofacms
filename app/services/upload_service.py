from app.utils.file_upload import save_image


class UploadService:

    @staticmethod
    def image(file, folder):

        if not file:

            return None

        return save_image(
            file,
            folder
        )