from flask import jsonify, render_template, request
from app import app, db
from app.models import CVE
from datetime import datetime, timedelta

@app.route('/cves/list')
def list_cves():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'published')  # Default to sorting by published date

    # Define valid sorting columns
    valid_sort_columns = {
        'published': CVE.published,
        'last_modified': CVE.last_modified,
        'status': CVE.status,
        'base_score_v2': CVE.base_score_v2,
        'base_score_v3': CVE.base_score_v3
    }

    # Get the sorting column
    sort_column = valid_sort_columns.get(sort_by, CVE.published)

    # Query with sorting
    cves = CVE.query.order_by(sort_column).paginate(page=page, per_page=per_page)
    return render_template('index.html', cves=cves)
@app.route('/api/cves')
def get_cves():
    # Filter parameters
    cve_id = request.args.get('cve_id')
    year = request.args.get('year')
    score = request.args.get('score')
    last_modified_days = request.args.get('last_modified')
    
    query = CVE.query
    
    if cve_id:
        query = query.filter(CVE.id == cve_id)
    if year:
        query = query.filter(CVE.id.like(f'CVE-{year}-%'))
    if score:
        query = query.filter((CVE.base_score_v2 >= float(score)) | (CVE.base_score_v3 >= float(score)))
    if last_modified_days:
        cutoff_date = datetime.now() - timedelta(days=int(last_modified_days))
        query = query.filter(CVE.last_modified >= cutoff_date)
    
    cves = query.all()
    return jsonify([{
        'id': cve.id,
        'published': cve.published,
        'last_modified': cve.last_modified,
        'description': cve.description,
        'base_score_v2': cve.base_score_v2,
        'base_score_v3': cve.base_score_v3
    } for cve in cves])

@app.route('/cves/<cve_id>')
def cve_detail(cve_id):
    cve = CVE.query.get_or_404(cve_id)
    return render_template('cve_detail.html', 
                         cve=cve,
                         cvss_v2_metrics=parse_cvss_vector(cve.cvss_v2_vector),
                         cvss_v3_metrics=parse_cvss_vector(cve.cvss_v3_vector))

def parse_cvss_vector(vector_string):
    if not vector_string:
        return {}
    return {part.split(':')[0]: part.split(':')[1] 
            for part in vector_string.split('/')}

