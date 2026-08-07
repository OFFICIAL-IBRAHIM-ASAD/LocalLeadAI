from app.database.db import get_connection


class DatabaseManager:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def add_business(
        self,
        name,
        category,
        phone,
        website,
        rating,
        reviews,
        address,
        maps_url,
    ):
        """
        Adds a business if it doesn't already exist.
        """

        self.cursor.execute("""
            INSERT OR IGNORE INTO businesses
            (
                name,
                category,
                phone,
                website,
                rating,
                reviews,
                address,
                maps_url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            category,
            phone,
            website,
            rating,
            reviews,
            address,
            maps_url
        ))

        self.conn.commit()

    def get_all_businesses(self):
        self.cursor.execute("SELECT * FROM businesses")
        return self.cursor.fetchall()

    def get_businesses_without_websites(self):
        self.cursor.execute("""
            SELECT *
            FROM businesses
            WHERE website IS NULL
               OR website = ''
        """)
        return self.cursor.fetchall()

    def mark_contacted(self, business_id):
        self.cursor.execute("""
            UPDATE businesses
            SET contacted = 1
            WHERE id = ?
        """, (business_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()