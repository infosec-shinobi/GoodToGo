from pathlib import Path

from fastapi.testclient import TestClient

from app.content.catalog import load_catalog
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
    assert 'id="device-save" type="checkbox"' in response.text
    assert 'id="device-save-status"' in response.text
    assert "Device saving is off" in response.text
    assert 'id="inactivity-status"' in response.text
    assert "30 minutes of inactivity" in response.text
    assert "Closing this tab also loses unsaved answers" in response.text
    assert "Get professional guidance" in response.text
    assert "wills, trusts, powers of attorney" in response.text
    assert 'aria-label="Workbook sections"' in response.text
    assert "Estimated time:" in response.text
    assert "Safe note, location, or next step" in response.text
    assert "__note" in response.text
    assert "professional_help" in response.text
    assert "Need professional help" in response.text
    assert 'data-response-type="applicability"' in response.text
    assert 'data-applies-question="dependents.exists"' in response.text
    assert 'id="print-workbook"' in response.text
    assert 'id="print-tasks"' in response.text
    assert "method=" not in response.text
    assert "action=" not in response.text


def test_private_javascript_only_fetches_the_public_catalog():
    script = (PROJECT_ROOT / "app/static/js/workbook.js").read_text(encoding="utf-8")

    assert script.count("fetch(") == 1
    assert 'fetch("/api/v1/catalog"' in script
    assert "localStorage" in script
    assert "saveToggle.checked" in script
    assert "updateSaveStatus" in script
    assert "Device saving is off" in script
    assert "idleWarningMs" in script
    assert "idleClearMs" in script
    assert "clearSession" in script
    assert "30 minutes of inactivity" in script
    assert "applyConditionals" in script
    assert "needsProfessionalHelp" in script
    assert "professional help flagged" in script
    assert "taskCustomizations" in script
    assert "Include in take-home list" in script
    assert "adjustable priority" in script
    assert "getReadinessAnswers" in script
    assert "getFormState" in script


def test_private_workbook_has_responsive_css_hooks():
    stylesheet = (PROJECT_ROOT / "app/static/css/app.css").read_text(encoding="utf-8")

    assert "@media (max-width: 760px)" in stylesheet
    assert ".workbook-toolbar" in stylesheet
    assert ".choice-grid" in stylesheet
    assert "grid-template-columns: 1fr 1fr" in stylesheet
    assert "scroll-margin-top" in stylesheet
    assert "@media print" in stylesheet
    assert ".print-take-home-only .workbook" in stylesheet
    assert ".task-item.excluded" in stylesheet
    assert ".task-controls" in stylesheet
    assert "focus-visible" in stylesheet


def test_blank_take_home_is_standalone_public_content():
    response = client.get("/private/take-home/blank")
    assert response.status_code == 200
    assert "Blank take-home list" in response.text
    assert response.text.count('class="task-item blank-task"') == 6
    assert "Responsible person:" in response.text
    assert "Target date:" in response.text
    assert "Safe notes / source reference:" in response.text
    assert "Source appendix" in response.text
    assert "not a live availability check" in response.text
    assert "workbook.js" not in response.text
    for resource in load_catalog().resources:
        assert str(resource.url) in response.text
        assert resource.last_verified in response.text
    assert load_catalog().workbook.version in response.text
    assert "Link last verified:" in response.text
    assert "Last reviewed:" in response.text
    assert "Jurisdiction:" in response.text


def test_personalized_take_home_print_and_privacy_hooks():
    page = client.get("/private").text
    stylesheet = (PROJECT_ROOT / "app/static/css/app.css").read_text(encoding="utf-8")
    assert 'href="/private/take-home/blank"' in page
    assert 'id="source-appendix-list"' in page
    assert "same opt-in device saving" in page
    assert "printer queues" in page
    assert ".task-assignment input:focus-visible" in stylesheet
    assert ".notes-lines" in stylesheet
    assert ".print-only" in stylesheet
    assert ".source-appendix" in stylesheet


def test_mvp0_decisions_are_documented():
    review = (PROJECT_ROOT / "docs/mvp0-review.md").read_text(encoding="utf-8")
    roadmap = (PROJECT_ROOT / "docs/roadmap.md").read_text(encoding="utf-8")
    guidance = (PROJECT_ROOT / "docs/professional-guidance.md").read_text(encoding="utf-8")

    for adr in (
        "0004-authentication-approach.md",
        "0005-persistent-encryption.md",
        "0006-pdf-rendering.md",
    ):
        assert (PROJECT_ROOT / "docs/adr" / adr).exists()

    assert "Complete for personal-project use" in review
    assert (
        "Status: Complete for personal-project use; professional validation not claimed"
        in roadmap
    )
    assert "Do not claim the content is legally reviewed" in review
    assert "When To Get Professional Guidance" in guidance
    assert "Legal Guidance" in guidance
    assert "Medical Guidance" in guidance
