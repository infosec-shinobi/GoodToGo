from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_public_pages_and_health_are_available():
    for path in ("/", "/private", "/settings"):
        response = client.get(path)
        assert response.status_code == 200
        assert "GoodToGo" in response.text

    assert client.get("/health").json() == {"status": "ok"}


def test_catalog_endpoint_exposes_only_public_content():
    response = client.get("/api/v1/catalog")
    body = response.json()

    assert response.status_code == 200
    assert set(body) == {"workbook", "resources"}
    assert "answers" not in response.text.lower()


def test_security_headers_are_present():
    response = client.get("/")

    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]


def test_private_workbook_has_no_submission_target():
    response = client.get("/private")

    assert 'id="private-workbook"' in response.text
    assert 'aria-label="Workbook sections"' in response.text
    assert "Estimated time:" in response.text
    assert "Safe note, location, or next step" in response.text
    assert "__note" in response.text
    assert 'id="print-workbook"' in response.text
    assert 'id="print-tasks"' in response.text
    assert "method=" not in response.text
    assert "action=" not in response.text


def test_private_javascript_only_fetches_the_public_catalog():
    script = (PROJECT_ROOT / "app/static/js/workbook.js").read_text(encoding="utf-8")

    assert script.count("fetch(") == 1
    assert 'fetch("/api/v1/catalog"' in script
    assert "localStorage" in script
    assert "getReadinessAnswers" in script
    assert "getFormState" in script
