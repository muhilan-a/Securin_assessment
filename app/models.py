from app import db,models
from datetime import datetime

class CVE(db.Model):
    __tablename__ = 'cve'
    id = db.Column(db.String(20), primary_key=True)
    published = db.Column(db.DateTime)
    last_modified = db.Column(db.DateTime)
    source_Identifier = db.Column(db.String(100))
    description = db.Column(db.Text)
    base_score_v2 = db.Column(db.Float)
    base_score_v3 = db.Column(db.Float)
    cvss_v2_vector = db.Column(db.String(100))
    cvss_v2_severity = db.Column(db.String(50))
    cvss_v3_vector = db.Column(db.String(100))
    cvss_v3_severity = db.Column(db.String(20))
    exploitability_score = db.Column(db.Float)
    impact_score = db.Column(db.Float)
    cpe_list = db.Column(db.JSON)
    status = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<CVE {self.id}>'