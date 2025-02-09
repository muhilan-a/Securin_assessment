from app import app, db
from app.models import CVE

with app.app_context():
    count = CVE.query.count()
    print(f"Total CVEs in database: {count}")