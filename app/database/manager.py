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
        Inserts a new business. Assumes the caller has already
        checked it doesn't exist (see get_by_maps_url).
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

        return self.cursor.rowcount > 0

    def get_by_maps_url(self, maps_url):
        self.cursor.execute(
            "SELECT id, phone, website FROM businesses WHERE maps_url = ?",
            (maps_url,),
        )
        return self.cursor.fetchone()

    def update_contact_info(self, business_id, phone, website):
        self.cursor.execute("""
            UPDATE businesses
            SET
                phone = COALESCE(NULLIF(phone, ''), ?),
                website = COALESCE(NULLIF(website, ''), ?)
            WHERE id = ?
        """, (phone, website, business_id))
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

    def get_uncontacted_leads(self):
        """Businesses with a phone, no website, not yet contacted,
        and not previously marked as a failed WhatsApp send."""
        self.cursor.execute("""
            SELECT *
            FROM businesses
            WHERE (website IS NULL OR website = '')
              AND phone IS NOT NULL AND phone != ''
              AND contacted = 0
              AND whatsapp_failed = 0
        """)
        return self.cursor.fetchall()

    def get_whatsapp_failed_leads(self):
        """Businesses whose WhatsApp send failed - candidates for
        cold calling instead."""
        self.cursor.execute("""
            SELECT *
            FROM businesses
            WHERE whatsapp_failed = 1
        """)
        return self.cursor.fetchall()

    def mark_contacted(self, business_id):
        self.cursor.execute("""
            UPDATE businesses
            SET contacted = 1
            WHERE id = ?
        """, (business_id,))
        self.conn.commit()

    def mark_whatsapp_failed(self, business_id):
        """Marks a business as failed-to-send, so it won't be
        retried in future campaigns. It'll instead show up in the
        cold-call export."""
        self.cursor.execute("""
            UPDATE businesses
            SET whatsapp_failed = 1
            WHERE id = ?
        """, (business_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()
