from app import db, models  # Ensure this import is at the top

def save_cve(cve_data):
    try:
        cve = models.CVE(
            id=cve_data['id'],
            published=cve_data['published'],
            last_modified=cve_data['last_modified'],
            description=cve_data['description'],
            base_score_v2=cve_data.get('base_score_v2'),
            base_score_v3=cve_data.get('base_score_v3'),
            cvss_v2_vector=cve_data.get('cvss_v2_vector'),
            cvss_v2_severity=cve_data.get('cvss_v2_severity'),
            cvss_v3_vector=cve_data.get('cvss_v3_vector'),
            cvss_v3_severity=cve_data.get('cvss_v3_severity'),
            exploitability_score=cve_data.get('exploitability_score'),
            impact_score=cve_data.get('impact_score'),
            cpe_list=cve_data.get('cpe_list'),
            status = cve_data.get('vulnStatus')
        )
        db.session.add(cve)
        db.session.commit()
    except Exception as e:
        print(f"Failed to save CVE {cve_data.get('id')}: {str(e)}")
        db.session.rollback()