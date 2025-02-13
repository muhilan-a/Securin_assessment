import pytest
import json
from datetime import datetime
from app import create_app, db
from app.models import CVE

python
Copy
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Add test data
        test_cve = CVE(
            id='CVE-2023-5678',
            published=datetime(2023, 1, 1, 12, 0, 0),
            last_modified=datetime(2023, 1, 2, 12, 0, 0),
            description='Test route vulnerability',
            base_score_v2=9.8,
            status='Confirmed'
        )
        db.session.add(test_cve)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_cves(client):
    # Test GET /cves/list
    response = client.get('/cves/list')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify response structure
    assert 'items' in data
    assert 'total' in data
    assert len(data['items']) > 0
    
    # Verify test data exists
    test_item = next((item for item in data['items'] if item['id'] == 'CVE-2023-5678'), None)
    assert test_item is not None
    assert test_item['base_score_v2'] == 9.8

def test_get_cve_detail(client):
    # Test GET /cves/CVE-2023-5678
    response = client.get('/cves/CVE-2023-5678')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['id'] == 'CVE-2023-5678'
    assert 'description' in data
    assert 'cvss_v2_vector' in data
    assert 'status' in data

def test_get_nonexistent_cve(client):
    # Test GET for non-existent CVE
    response = client.get('/cves/CVE-9999-9999')
    assert response.status_code == 404