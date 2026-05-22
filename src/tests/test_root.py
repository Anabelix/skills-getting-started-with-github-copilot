"""
Tests for the root endpoint (GET /).

The root endpoint should redirect to the static index.html page.
"""

import pytest


def test_root_redirect(client):
    """Test that GET / redirects to /static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_root_redirect_follow(client):
    """Test that following the redirect works (integration test)"""
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200
