from Database.connection import get_connection


class HistoryRepo:
    def add_record(
        self, input_text: str, output_text: str, probability: float, user_id: int
    ) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO requests_records (input, prediction, probability, user_id)
                VALUES (?, ?, ?, ?)
            """,
                (input_text, output_text, probability, user_id),
            )
            conn.commit()
