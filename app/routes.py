from flask import jsonify, render_template, request
from app import app, db
from app.models import CVE
from datetime import datetime, timedelta
from flasgger import swag_from 
@app.route('/cves/list')
@swag_from({
    'tags': ['CVEs'],
    'description': 'List all CVEs with pagination',
    'parameters': [
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'description': 'Page number (default: 1)'
        },
        {
            'name': 'per_page',
            'in': 'query',
            'type': 'integer',
            'description': 'Items per page (default: 10)'
        }
    ],
    'responses': {
        200: {
            'description': 'List of CVEs',
            'examples': {
                'application/json': [
                    {
                        'id': 'CVE-1999-0334',
                        'published': '1999-02-01T00:00:00',
                        'status': 'Modified'
                    }
                ]
            }
        }
    }
})
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
@swag_from({
    'tags': ['CVEs'],
    'description': 'Get details of a specific CVE by ID.',
    'parameters': [
        {
            'name': 'cve_id',
            'in': 'path',
            'type': 'string',
            'description': 'The ID of the CVE to retrieve',
            'required': True
        }
    ],
    'responses': {
        200: {
            'description': 'Details of the specified CVE',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string'},
                    'published': {'type': 'string', 'format': 'date-time'},
                    'last_modified': {'type': 'string', 'format': 'date-time'},
                    'description': {'type': 'string'},
                    'base_score_v2': {'type': 'number'},
                    'base_score_v3': {'type': 'number'},
                    'cvss_v2_vector': {'type': 'string'},
                    'cvss_v2_severity': {'type': 'string'},
                    'cvss_v3_vector': {'type': 'string'},
                    'cvss_v3_severity': {'type': 'string'},
                    'exploitability_score': {'type': 'number'},
                    'impact_score': {'type': 'number'},
                    'cpe_list': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'criteria': {'type': 'string'},
                                'vulnerable': {'type': 'boolean'}
                            }
                        }
                    },
                    'status': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'CVE not found'
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

