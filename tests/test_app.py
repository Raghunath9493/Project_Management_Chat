import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from flask import Flask, session
from unittest.mock import patch, MagicMock
from routes.routes import register_routes

@pytest.fixture
def client():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/test_db'
    with app.test_client() as client:
        with app.app_context():
            register_routes(app)
        yield client

@patch('routes.routes.MongoClient')
def test_register_missing_data(mock_mongo, client):
    response = client.post('/register', data=dict(email="", password=""))
    assert response.status_code == 400
    assert b'Email and password are required' in response.data

@patch('routes.routes.MongoClient')
def test_login_invalid_credentials(mock_mongo, client):
    mock_db = MagicMock()
    mock_db.users.find_one.return_value = None
    mock_mongo().get_database().return_value = mock_db

def test_dashboard_route_not_logged_in(client):
    response = client.get('/dashboard')
    assert response.status_code == 302  # redirect to home
    assert response.location.endswith('/')

def test_logout_route(client):
    with client.session_transaction() as sess:
        sess['email'] = 'test@example.com'
    response = client.get('/logout')
    assert response.status_code == 200
    assert b'Logged out successfully' in response.data
    with client.session_transaction() as sess:
        assert 'email' not in sess

def test_budget_form_route_not_logged_in(client):
    response = client.get('/budgetform')
    assert response.status_code == 302  # redirect to home
    assert response.location.endswith('/')

@patch('routes.routes.MongoClient')
def test_get_budget_data_not_logged_in(mock_mongo, client):
    response = client.get('/api/budget_data')
    assert response.status_code == 401
    assert b'Unauthorized' in response.data

#testing for unit test