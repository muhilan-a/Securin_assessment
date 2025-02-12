import sys
import os
import time
from datetime import datetime

# Add the root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.nvd_api import fetch_cves, parse_cve_data
from app.services.database import save_cve
from app import app, db

def sync_cves():
    start_index = 0
    results_per_page = 50  # Start with smaller batches
    total_inserted = 0
    total_skipped = 0

    with app.app_context():
        while True:
            try:
                print(f"Fetching {results_per_page} records from index {start_index}...")

                # Fetch data from NVD API
                data = fetch_cves(start_index, results_per_page)
                if not data or 'vulnerabilities' not in data:
                    print("No more CVEs found or invalid API response")
                    break

                # Process each CVE
                for cve_item in data['vulnerabilities']:
                    cve_data = parse_cve_data(cve_item)
                    if cve_data:  # Only save if parsing succeeded
                        try:
                            save_cve(cve_data)
                            total_inserted += 1
                        except Exception as e:
                            print(f"Failed to save CVE {cve_data.get('id')}: {str(e)}")
                            db.session.rollback()
                            total_skipped += 1
                    else:
                        total_skipped += 1

                # Commit after each batch
                db.session.commit()
                print(f"Inserted {total_inserted} CVEs, skipped {total_skipped} CVEs so far")

                # Update start index and respect API rate limits
                start_index += results_per_page
                time.sleep(6)  # NVD requires 6s between requests

            except Exception as e:
                print(f"Fatal error: {str(e)}")
                db.session.rollback()
                break

if __name__ == "__main__":
    sync_cves()
    print("Sync completed")

