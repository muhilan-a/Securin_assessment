from flask import jsonify, render_template, request
from app import app, db
from app.models import CVE
from datetime import datetime, timedelta
from flasgger import swag_from 
@app.route('/cves/list')
@swag_from({
    'tags': ['CVEs'],
    'description': 'Get a paginated list of CVEs with filtering and sorting options.',
    'parameters': [
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'default': 1,
            'description': 'Page number for pagination.'
        },
        {
            'name': 'per_page',
            'in': 'query',
            'type': 'integer',
            'default': 10,
            'description': 'Number of CVEs per page.'
        },
        {
            'name': 'cve_id',
            'in': 'query',
            'type': 'string',
            'description': 'Filter by exact CVE ID.'
        },
        {
            'name': 'year',
            'in': 'query',
            'type': 'integer',
            'description': 'Filter by CVE publication year.'
        },
        {
            'name': 'score',
            'in': 'query',
            'type': 'number',
            'description': 'Filter by minimum CVSS score (v2 or v3).'
        },
        {
            'name': 'last_modified_days',
            'in': 'query',
            'type': 'integer',
            'description': 'Filter by CVEs modified in the last N days.'
        },
        {
            'name': 'sort_by',
            'in': 'query',
            'type': 'string',
            'enum': ['published', 'last_modified', 'base_score_v2', 'base_score_v3'],
            'default': 'published',
            'description': 'Sort by field.'
        }
    ],
    'responses': {
        200: {
            'description': 'A paginated list of CVEs.',
            'schema': {
                '$ref': '#/definitions/CVEListResponse'
            }
        },
        400: {
            'description': 'Invalid input parameters.'
        }
    }
})
def list_cves():
    # Get all parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'published')
    cve_id = request.args.get('cve_id')
    year = request.args.get('year')
    score = request.args.get('score')
    last_modified_days = request.args.get('last_modified_days')

    # Base query
    query = CVE.query

    # Apply filters
    if cve_id:
        query = query.filter(CVE.id == cve_id)
    if year:
        query = query.filter(CVE.id.like(f'CVE-{year}-%'))
    if score:
        score = float(score)
        query = query.filter(
            (CVE.base_score_v2 >= score) | 
            (CVE.base_score_v3 >= score)
        )
    if last_modified_days:
        cutoff_date = datetime.now() - timedelta(days=int(last_modified_days))
        query = query.filter(CVE.last_modified >= cutoff_date)

    # Apply sorting
    sort_mapping = {
        'published': CVE.published,
        'last_modified': CVE.last_modified,
        'status': CVE.status,
        'base_score_v2': CVE.base_score_v2,
        'base_score_v3': CVE.base_score_v3
    }
    total_records = query.count()
    
   
    sort_column = sort_mapping.get(sort_by, CVE.published)
    cves = query.order_by(sort_column).paginate(page=page, per_page=per_page)
    
    return render_template('index.html', 
                         cves=cves,
                         total_records=total_records,
                         current_filters=request.args)
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
@swag_from({
    'tags': ['CVEs'],
    'description': 'Get detailed information about a specific CVE.',
    'parameters': [
        {
            'name': 'cve_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'example': 'CVE-1999-0334'
        }
    ],
    'responses': {
        200: {
            'description': 'Detailed information about the CVE.',
            'schema': {
                '$ref': '#/definitions/CVEDetail'
            }
        },
        404: {
            'description': 'CVE not found.'
        }
    }
})
def cve_detail(cve_id):
    cve = CVE.query.get_or_404(cve_id)
    return render_template('cve_detail.html', 
                         cve=cve,
                         cvss_v2_metrics=parse_cvss_vector(cve.cvss_v2_vector),
                         cvss_v3_metrics=parse_cvss_vector(cve.cvss_v3_vector))

def parse_cvss_vector(vector_string):
    if not vector_string:
        return {}

    value_mappings = {
        'AV': {'L': 'Local', 'A': 'Adjacent Network', 'N': 'Network'},
        'AC': {'H': 'High', 'M': 'Medium', 'L': 'Low'},
        'Au': {'N': 'None', 'S': 'Single', 'M': 'Multiple'},
        'C': {'N': 'None', 'P': 'Partial', 'C': 'Complete'},
        'I': {'N': 'None', 'P': 'Partial', 'C': 'Complete'},
        'A': {'N': 'None', 'P': 'Partial', 'C': 'Complete'}
    }

    metrics = {}
    for part in vector_string.split('/'):
        if ':' in part:
            key, value = part.split(':')
            full_value = value_mappings.get(key, {}).get(value, value)
            metrics[key] = full_value

    return metrics
