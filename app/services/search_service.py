from sqlalchemy import or_


class SearchService:

    @staticmethod
    def apply(
        query,
        keyword,
        columns
    ):

        if not keyword:

            return query

        return query.filter(

            or_(

                *[

                    column.ilike(f"%{keyword}%")

                    for column in columns

                ]

            )

        )