class ActivityService:

    @staticmethod
    def log(

        user,

        action,

        module,

        description

    ):

        print(

            f"[{module}] "

            f"{user.username} "

            f"{action} "

            f"{description}"

        )