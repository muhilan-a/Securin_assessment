
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from datetime import datetime
from app import create_app, db
from app.models import CVE

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_cve_model(app):
    with app.app_context():
        # Create test data
        test_cve = CVE(
            id='CVE-2023-1234',
            published=datetime(2023, 1, 1, 12, 0, 0),
            last_modified=datetime(2023, 1, 2, 12, 0, 0),
            description='Test vulnerability',
            base_score_v2=7.5,
            base_score_v3=8.2,
            status='Analyzed'
        )
        
        # Add to database
        db.session.add(test_cve)
        db.session.commit()

        # Retrieve from database
        cve = CVE.query.get('CVE-2023-1234')

        # Assertions
        assert cve is not None
        assert cve.id == 'CVE-2023-1234'
        assert cve.published.year == 2023
        assert cve.base_score_v2 == 7.5
        assert cve.status == 'Analyzed'
        assert str(cve) == '<CVE CVE-2023-1234>'