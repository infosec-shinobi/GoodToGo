import base64
import hashlib
import io
import json
import os
import runpy
import socket
import threading
from pathlib import Path

import pytest
import uvicorn

from app.content.catalog import load_catalog
from app.main import app

playwright = pytest.importorskip("playwright.sync_api")
pytestmark = pytest.mark.browser


@pytest.fixture(scope="module")
def live_url():
    ready = threading.Event()

    class TestServer(uvicorn.Server):
        async def startup(self, sockets=None):
            await super().startup(sockets)
            ready.set()

    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    server = TestServer(uvicorn.Config(app, log_level="critical", access_log=False))
    thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
    thread.start()
    assert ready.wait(10), "Browser test server did not start"
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=10)
    sock.close()


@pytest.fixture
def browser():
    with playwright.sync_playwright() as driver:
        browser = driver.chromium.launch()
        yield browser
        browser.close()


def fill_passphrase(page, password, confirm=False):
    page.locator("#resume-password").fill(password)
    if confirm:
        page.locator("#resume-confirm").fill(password)


def upload(page, contents):
    page.locator("#resume-file").set_input_files(
        {"name": "private.gtg-resume", "mimeType": "application/json", "buffer": contents}
    )
    page.locator("#resume-replace").check()


@pytest.mark.parametrize("width", [390, 1440])
def test_resume_private_network_boundary_and_print(browser, live_url, width):
    pypdf = pytest.importorskip("pypdf")
    pytest.importorskip("cryptography")
    decrypt_resume = runpy.run_path(
        str(Path(__file__).resolve().parents[2] / "tools/recover_resume.py")
    )["decrypt_resume"]

    context = browser.new_context(viewport={"width": width, "height": 900}, accept_downloads=True)
    traffic, console, errors, sockets = [], [], [], []
    context.on("request", lambda request: traffic.append(
        (request.url, request.method, request.post_data, str(request.headers))
    ))
    page = context.new_page()
    page.on("console", lambda message: console.append(message.text))
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("websocket", lambda socket: sockets.append(socket.url))
    page.goto(live_url + "/private")
    playwright.expect(page.locator("#resume-export")).to_be_enabled()
    question = page.locator(".question-card").first
    question.locator('[value="not_sure"]').check()
    marker = "PRIVATE_BOUNDARY_CANARY_73f8"
    note = marker + "\nLast line of safe notes"
    password = "periwinkle orchard " + marker
    question.locator("textarea").fill(note)
    task = page.locator(".task-item").first
    task.locator('[data-task-control="responsiblePerson"]').fill(marker)
    task.locator('[data-task-control="targetDate"]').fill("2026-12-01")
    task.locator('[data-task-control="priority"]').select_option("low")
    task.locator('[data-task-control="responsiblePerson"]').press("Enter")
    page.locator("#device-save").check()
    page.reload()
    playwright.expect(page.locator("#resume-export")).to_be_enabled()
    playwright.expect(question.locator("textarea")).to_have_value(note)
    fill_passphrase(page, "weak", confirm=True)
    page.locator("#resume-export").click()
    playwright.expect(page.locator("#resume-status")).to_contain_text("at least 16")
    fill_passphrase(page, password, confirm=True)
    with page.expect_download(timeout=60000) as download_info:
        page.locator("#resume-export").click()
    download = download_info.value
    assert download.suggested_filename == "goodtogo-private.gtg-resume"
    contents = download.path().read_bytes()
    assert marker.encode() not in contents
    recovered = decrypt_resume(contents, password)
    assert recovered["state"][question.get_attribute("data-question-id")] == "not_sure"
    playwright.expect(page.locator("#resume-password")).to_have_value("")

    # Wrong passwords and malformed files leave both current answers and storage intact.
    upload(page, contents)
    fill_passphrase(page, "wrong password")
    page.locator("#resume-import").click()
    playwright.expect(page.locator("#resume-status")).to_contain_text("incorrect", timeout=60000)
    playwright.expect(question.locator("textarea")).to_have_value(note)
    playwright.expect(page.locator("#device-save")).to_be_checked()
    upload(page, b'{"version":999}')
    fill_passphrase(page, password)
    page.locator("#resume-import").click()
    playwright.expect(page.locator("#resume-status")).to_contain_text("failed")
    playwright.expect(page.locator("#device-save")).to_be_checked()

    # Offline after initial assets: import and print require no request to the app.
    context.set_offline(True)
    page.locator("#clear-answers").click()
    upload(page, contents)
    fill_passphrase(page, password)
    page.locator("#resume-import").click()
    playwright.expect(page.locator("#resume-status")).to_contain_text(
        "Resume file loaded", timeout=60000
    )
    playwright.expect(question.locator("textarea")).to_have_value(note)
    playwright.expect(page.locator("#device-save")).not_to_be_checked()
    playwright.expect(page.locator('[data-task-control="responsiblePerson"]').first).to_have_value(marker)
    assert page.evaluate("localStorage.getItem('goodtogo.private.answers.v1')") is None

    page.emulate_media(media="print", color_scheme="dark")
    pdf = page.pdf(format="Letter", print_background=False)
    pdf_text = "\n".join(p.extract_text() for p in pypdf.PdfReader(io.BytesIO(pdf)).pages)
    assert marker in pdf_text and "Last line of safe notes" in pdf_text
    assert "Answer: Not sure" in pdf_text
    assert "2026-12-01" in pdf_text and "Source appendix" in pdf_text
    page.emulate_media(media="screen")
    page.locator("#clear-answers").click()
    assert page.locator(".printed-answer").count() == 0
    playwright.expect(question.locator("textarea")).to_have_value("")
    playwright.expect(page.locator("#task-list")).to_be_empty()
    # A clear during KDF work must not resurrect answers.
    upload(page, contents)
    fill_passphrase(page, password)
    page.locator("#resume-import").click()
    page.locator("#clear-answers").click()
    playwright.expect(page.locator("#resume-import")).to_be_enabled(timeout=60000)
    playwright.expect(question.locator("textarea")).to_have_value("")

    assert not errors and not sockets
    assert marker not in " ".join(console)
    allowed = {"/private", "/api/v1/catalog", "/static/js/theme-init.js",
               "/static/js/workbook.js", "/static/js/resume-crypto.js",
               "/static/js/resume-worker.js",
               "/static/vendor/scrypt-3.0.1.js", "/static/css/app.css", "/favicon.ico"}
    for url, method, body, headers in traffic:
        assert marker not in url + (body or "") + headers
        assert method == "GET" and body is None
        assert url.startswith(live_url) and url.removeprefix(live_url) in allowed
    context.close()


def test_blank_workbook_print_is_independent_of_saved_answers(browser, live_url):
    pypdf = pytest.importorskip("pypdf")
    context = browser.new_context()
    page = context.new_page()
    page.goto(live_url + "/private")
    page.evaluate(
        "localStorage.setItem('goodtogo.private.answers.v1', "
        "JSON.stringify({'x':'PRIVATE_SENTINEL'}))"
    )
    page.goto(live_url + "/private/workbook/blank")
    assert page.locator(".blank-question").count() > 20
    assert page.locator('script[src*="workbook.js"]').count() == 0
    pdf = page.pdf(format="Letter")
    text = "\n".join(p.extract_text() for p in pypdf.PdfReader(io.BytesIO(pdf)).pages)
    assert "PRIVATE_SENTINEL" not in text
    normalized = " ".join(text.split())
    assert "Blank readiness workbook" in normalized and "Source appendix" in normalized
    assert "Conditional question" in text
    saved = page.evaluate("localStorage.getItem('goodtogo.private.answers.v1')")
    assert "PRIVATE_SENTINEL" in saved
    context.close()


def test_private_accessibility_and_keyboard(browser, live_url):
    axe = Path(__file__).resolve().parents[2] / "node_modules/axe-core/axe.min.js"
    if not axe.exists():
        pytest.skip("Run npm ci to install the pinned local accessibility test dependency")
    context = browser.new_context(viewport={"width": 390, "height": 900})
    page = context.new_page()
    for path in ("/private", "/private/workbook/blank", "/private/take-home/blank"):
        page.goto(live_url + path)
        if path == "/private":
            playwright.expect(page.locator("#resume-export")).to_be_enabled()
            page.locator("#resume-password").focus()
            page.keyboard.press("Tab")
            playwright.expect(page.locator("#resume-confirm")).to_be_focused()
            page.keyboard.press("Tab")
            playwright.expect(page.locator("#resume-export")).to_be_focused()
            # Include generated assignment controls in the scan.
            page.locator('.question-card [value="not_sure"]').first.check()
        page.evaluate(axe.read_text(encoding="utf-8"))
        results = page.evaluate(
            "async () => (await axe.run(document, {"
            "runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa']}"
            "})).violations.map(v => ({id:v.id, nodes:v.nodes.map(n => n.target)}))"
        )
        assert results == [], results
    context.close()


def test_independent_writer_and_authenticated_invalid_payloads(browser, live_url):
    pytest.importorskip("cryptography")
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    workbook = load_catalog().workbook
    question_id = workbook.sections[0].questions[0].id
    password = "willow graphite apricot otter spruce"
    salt = os.urandom(16)
    key = hashlib.scrypt(
        password.encode(), salt=salt, n=131072, r=8, p=1,
        dklen=32, maxmem=256 * 1024 * 1024,
    )

    def make_file(state, version=workbook.version):
        iv = os.urandom(12)
        payload = {"schema": 1, "pack": {"id": workbook.id, "version": version},
                   "createdAt": "2026-11-05T12:00:00Z", "state": state}
        encrypted = AESGCM(key).encrypt(
            iv, json.dumps(payload).encode(), b"goodtogo.private-resume/v1"
        )
        def b64(value):
            return base64.b64encode(value).decode("ascii")

        return json.dumps({
            "format": "goodtogo.private-resume", "version": 1,
            "kdf": {"name": "scrypt", "N": 131072, "r": 8, "p": 1, "salt": b64(salt)},
            "cipher": {"name": "AES-256-GCM", "iv": b64(iv)}, "ciphertext": b64(encrypted),
        }).encode()

    context = browser.new_context()
    page = context.new_page()
    page.goto(live_url + "/private")
    playwright.expect(page.locator("#resume-export")).to_be_enabled()
    note = page.locator(".question-card textarea").first
    note.fill("Keep current answers")
    for contents, expected in [
        (make_file({question_id: "invalid-state"}), "operation failed"),
        (make_file({}, version="unsupported-version"), "different content pack"),
    ]:
        upload(page, contents)
        fill_passphrase(page, password)
        page.locator("#resume-import").click()
        playwright.expect(page.locator("#resume-status")).to_contain_text(expected, timeout=60000)
        playwright.expect(note).to_have_value("Keep current answers")
    upload(page, make_file({question_id: "not_sure", question_id + "__note": "Recovered 🐾"}))
    fill_passphrase(page, password)
    page.locator("#resume-import").click()
    playwright.expect(page.locator("#resume-status")).to_contain_text("file loaded", timeout=60000)
    playwright.expect(note).to_have_value("Recovered 🐾")
    context.close()


def test_resume_controls_fail_closed_without_webcrypto(browser, live_url):
    context = browser.new_context()
    context.add_init_script("Object.defineProperty(window, 'crypto', {value: {}})")
    page = context.new_page()
    page.goto(live_url + "/private")
    playwright.expect(page.locator("#resume-status")).to_contain_text("Use HTTPS or localhost")
    playwright.expect(page.locator("#resume-export")).to_be_disabled()
    playwright.expect(page.locator("#resume-import")).to_be_disabled()
    page.locator('.question-card [value="not_sure"]').first.check()
    assert page.locator(".task-item").count() == 1
    context.close()
