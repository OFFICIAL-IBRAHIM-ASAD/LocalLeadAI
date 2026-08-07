from app.database.db import create_tables
from app.database.manager import DatabaseManager

create_tables()

db = DatabaseManager()

db.add_business(
    name="Test Restaurant",
    category="Restaurant",
    phone="+923001234567",
    website="",
    rating=4.5,
    reviews=120,
    address="Karachi",
    maps_url="https://maps.google.com/test"
)

businesses = db.get_all_businesses()

for business in businesses:
    print(business)

db.close()