from app import app, db, models

def deduplicate_cves():
    with app.app_context():
        # Find duplicate CVE IDs
        duplicates = db.session.query(
            models.CVE.id
        ).group_by(models.CVE.id).having(db.func.count() > 1).all()

        for (cve_id,) in duplicates:
            # Get all duplicates for this CVE ID
            records = models.CVE.query.filter_by(id=cve_id).all()
            
            # Keep the most recently modified record
            latest = max(records, key=lambda x: x.last_modified)
            
            # Delete others
            for record in records:
                if record != latest:
                    db.session.delete(record)
            
            db.session.commit()
            print(f"Removed {len(records)-1} duplicates for {cve_id}")

if __name__ == "__main__":
    deduplicate_cves()