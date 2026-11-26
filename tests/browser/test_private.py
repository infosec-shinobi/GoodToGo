import base64
import hashlib
import io
import json
import os
import runpy
import socket
import threading
from pathlib import Path
from urllib.parse import urlsplit

import pytest
import uvicorn

from app.content.catalog import load_catalog
from app.main import app

playwright = pytest.importorskip("playwright.sync_api")
pytestmark = pytest.mark.browser

BRAND_ASSET_PATHS = {
    "/static/branding/brand-tokens.css",
    "/static/branding/logos/goodtogo-horizontal.svg",
    "/static/branding/logos/goodtogo-horizontal-dark.svg",
    "/static/branding/logos/goodtogo-symbol-monochrome.svg",
    "/static/branding/icons/life-plan.svg",
    "/static/branding/icons/family.svg",
    "/static/branding/icons/legal.svg",
    "/static/branding/icons/financial.svg",
    "/static/branding/icons/digital.svg",
    "/static/branding/icons/documents.svg",
    "/static/branding/icons/legacy.svg",
    "/static/branding/favicons/goodtogo-favicon.svg",
    "/static/branding/favicons/favicon-32.png",
    "/static/branding/favicons/favicon.ico",
    "/static/branding/favicons/favicon-180.png",
    "/static/fonts/Manrope-variable.ttf",
    "/static/fonts/Inter-variable.ttf",
}


def checked_public_path(url):
    """Allow only the exact public stylesheet content versions, never arbitrary queries."""
    parsed = urlsplit(url)
    styles = {"/static/css/app.css", "/static/branding/brand-tokens.css"}
    if parsed.path in styles:
        file = Path(__file__).resolve().parents[2] / "app" / parsed.path.lstrip("/")
        expected = hashlib.sha256(file.read_bytes()).hexdigest()[:12]
        assert parsed.query == f"v={expected}"
    else:
        assert not parsed.query
    return parsed.path


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
    playwright.expect(page.locator(".print-brand")).to_be_visible()
    assert page.locator(".print-brand").evaluate(
        "element => getComputedStyle(element).display"
    ) == "flex"
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
    allowed |= BRAND_ASSET_PATHS
    for url, method, body, headers in traffic:
        assert marker not in url + (body or "") + headers
        assert method == "GET" and body is None
        assert url.startswith(live_url) and checked_public_path(url) in allowed
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
    assert page.locator(".print-brand img").get_attribute("src").endswith(
        "goodtogo-symbol-monochrome.svg"
    )
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


def color_contrast(first, second):
    def luminance(rgb):
        channels = [value / 255 for value in rgb]
        linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels]
        weights = zip(linear, [0.2126, 0.7152, 0.0722], strict=True)
        return sum(value * weight for value, weight in weights)

    a, b = sorted([luminance(first), luminance(second)])
    return (b + 0.05) / (a + 0.05)


def test_brand_theme_preferences_system_changes_and_reduced_motion(browser, live_url):
    context = browser.new_context(color_scheme="light", viewport={"width": 390, "height": 900})
    page = context.new_page()
    page.goto(live_url + "/settings")
    page.locator('[name="theme-mode"][value="dark"]').check()
    page.locator('[name="color-scheme"][value="forest"]').check()
    page.get_by_role("link", name="GoodToGo home").click()
    playwright.expect(page.locator("html")).to_have_attribute("data-theme", "dark")
    playwright.expect(page.locator("html")).to_have_attribute("data-scheme", "forest")
    dark_bg = page.locator("body").evaluate("element => getComputedStyle(element).backgroundColor")
    playwright.expect(page.locator(".brand-dark")).to_be_visible()
    page.emulate_media(color_scheme="light")
    assert page.locator("body").evaluate(
        "element => getComputedStyle(element).backgroundColor"
    ) == dark_bg
    page.goto(live_url + "/settings")
    page.locator('[name="theme-mode"][value="system"]').check()
    page.get_by_role("link", name="GoodToGo home").click()
    assert page.locator("body").evaluate(
        "element => getComputedStyle(element).backgroundColor"
    ) != dark_bg
    page.emulate_media(color_scheme="dark")
    playwright.expect(page.locator(".brand-dark")).to_be_visible()
    assert page.locator("body").evaluate(
        "element => getComputedStyle(element).backgroundColor"
    ) == dark_bg
    assert page.evaluate("localStorage.getItem('fr-color-scheme')") == "forest"
    assert page.evaluate("localStorage.getItem('goodtogo.private.answers.v1')") is None
    page.emulate_media(reduced_motion="reduce")
    page.goto(live_url + "/private")
    assert page.locator(".progress-bar").evaluate(
        "element => getComputedStyle(element).transitionDuration"
    ) == "0s"
    context.close()


@pytest.mark.parametrize("width", [390, 1440])
def test_branding_themes_contrast_and_local_assets(browser, live_url, width):
    axe = Path(__file__).resolve().parents[2] / "node_modules/axe-core/axe.min.js"
    if not axe.exists():
        pytest.skip("Run npm ci for the pinned local accessibility checker")
    allowed = BRAND_ASSET_PATHS | {
        "/", "/private", "/settings", "/api/v1/catalog", "/static/js/theme-init.js",
        "/static/js/settings.js", "/static/css/app.css", "/static/js/workbook.js",
        "/static/js/resume-crypto.js", "/static/vendor/scrypt-3.0.1.js",
    }
    for mode, media in [("light", "light"), ("dark", "dark"),
                        ("system", "light"), ("system", "dark")]:
        for scheme in ("ocean", "forest", "ember", "plum", "slate"):
            context = browser.new_context(
                viewport={"width": width, "height": 900}, color_scheme=media
            )
            context.add_init_script(
                f"localStorage.setItem('fr-theme-mode', '{mode}');"
                f"localStorage.setItem('fr-color-scheme', '{scheme}');"
            )
            traffic, failures, startup = [], [], []
            context.on("request", lambda request, entries=traffic: entries.append(request))
            context.on("response", lambda response, entries=failures: entries.append(response.url)
                       if response.status >= 400 else None)
            page = context.new_page()
            def capture_startup(page=page, entries=startup):
                entries.append(page.evaluate(
                    "[document.documentElement.dataset.theme,"
                    "document.documentElement.dataset.scheme]"
                ))

            page.on("domcontentloaded", capture_startup)
            page.goto(live_url + "/")
            page.evaluate("document.fonts.ready")
            # DOMContentLoaded may precede CSS completion; cached attributes must
            # already be set, and render-blocking CSS chooses the correct artwork.
            assert startup[0] == [mode, scheme]
            logo = page.locator(".brand img:visible")
            playwright.expect(logo).to_be_visible()
            assert page.locator(".hero img").count() == 0
            logo_box = logo.bounding_box()
            assert logo_box["width"] <= 130 and logo_box["height"] <= 52
            assert abs(logo_box["width"] / logo_box["height"] - 2.5) < 0.01
            assert page.locator(".card .section-icons img").count() == 6
            for icon in page.locator(".card .section-icons img").all():
                box = icon.bounding_box()
                assert box["width"] == box["height"] == 30
            assert page.evaluate("document.fonts.check('16px Manrope')")
            assert page.evaluate("document.fonts.check('16px Inter')")
            assert page.evaluate(
                "Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)"
            )
            assert page.evaluate(
                "document.documentElement.scrollWidth <= window.innerWidth"
            ), (width, mode, scheme)
            logo_bg = page.evaluate(
                "getComputedStyle(document.querySelector('.brand')).backgroundColor"
            )
            assert logo_bg == ("rgba(0, 0, 0, 0)" if media == "dark" else "rgb(255, 255, 255)")
            expected_logo = "brand-dark" if media == "dark" else "brand-light"
            assert logo.get_attribute("class") == expected_logo
            colors = page.evaluate(r"""() => {
              const result = {};
              const probe = document.createElement('span');
              document.body.append(probe);
              for (const name of ['text','text-muted','heading','bg','surface','surface-muted',
                'accent','on-accent','accent-soft','accent-ink','danger',
                'control-border','progress']) {
                probe.style.color = `var(--${name})`;
                result[name] = getComputedStyle(probe).color.match(/[\d.]+/g).map(Number);
              }
              probe.remove();
              return result;
            }""")
            for foreground, background, minimum in [
                ("text", "bg", 4.5), ("text", "surface", 4.5),
                ("text-muted", "surface-muted", 4.5), ("heading", "surface", 4.5),
                ("accent", "bg", 4.5), ("accent", "surface-muted", 4.5),
                ("on-accent", "accent", 4.5), ("accent-ink", "accent-soft", 4.5),
                ("danger", "surface-muted", 4.5), ("control-border", "surface-muted", 3),
                ("progress", "surface-muted", 3),
            ]:
                ratio = color_contrast(colors[foreground], colors[background])
                assert ratio >= minimum, (mode, scheme, foreground, background, ratio)
            # Full scans on home, plus interactive pages in explicit light/dark modes.
            paths = ["/"] if mode == "system" else ["/", "/private", "/settings"]
            for path in paths:
                if path != "/":
                    # The startup handler above applies only to the home page.
                    page.remove_listener("domcontentloaded", capture_startup)
                    page.goto(live_url + path)
                if path == "/private":
                    playwright.expect(page.locator("#resume-export")).to_be_enabled()
                    page.locator('.question-card [value="not_sure"]').first.check()
                page.evaluate(axe.read_text(encoding="utf-8"))
                violations = page.evaluate(
                    "async () => (await axe.run(document, {runOnly: {type:'tag',"
                    "values:['wcag2a','wcag2aa','wcag21aa']}})).violations.map(v=>({"
                    "id:v.id,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))"
                )
                assert violations == [], (path, mode, scheme, violations)
            for request in traffic:
                assert request.url.startswith(live_url)
                assert checked_public_path(request.url) in allowed
                assert request.method == "GET" and request.post_data is None
            assert failures == []
            context.close()


def test_branding_responsive_geometry(browser, live_url):
    context = browser.new_context()
    page = context.new_page()
    columns, sizes = {}, {}
    for width in (320, 390, 600, 768, 1024, 1440, 1920):
        page.set_viewport_size({"width": width, "height": 900})
        for path in ("/", "/private"):
            page.goto(live_url + path)
            page.evaluate("document.fonts.ready")
            assert page.evaluate(
                "document.documentElement.scrollWidth <= innerWidth"
            ), (width, path)
            logo = page.locator(".brand img:visible").bounding_box()
            assert logo["width"] <= 130 and logo["height"] <= 52
            if path == "/":
                assert page.locator(".hero img").count() == 0
                columns[width] = page.locator(".card-grid").evaluate(
                    "element => getComputedStyle(element).gridTemplateColumns.split(' ').length"
                )
                sizes[width] = page.locator(".hero h1").evaluate(
                    "element => parseFloat(getComputedStyle(element).fontSize)"
                )
                for card in page.locator(".card").all():
                    assert card.locator(".section-icons img").count() == 1
                    icon = card.locator(".section-icons").bounding_box()
                    assert icon["width"] == icon["height"] == 40
            else:
                playwright.expect(page.locator("#resume-export")).to_be_enabled()
                for icon in page.locator(".section-nav .section-icons").all():
                    bounds = icon.bounding_box()
                    assert bounds["width"] == bounds["height"] == 32
    assert columns[320] == columns[390] == 1
    assert columns[768] == 2 and columns[1440] == columns[1920] == 3
    assert sizes[320] < sizes[768] < sizes[1440]
    context.close()
