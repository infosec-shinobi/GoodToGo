import hashlib
import re
from pathlib import Path
from xml.etree import ElementTree

from fastapi.testclient import TestClient

from app.main import app

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "app/static"
client = TestClient(app)


def test_packaged_brand_assets_match_source_masters_and_are_served():
    assets = list((STATIC / "branding").rglob("*"))
    assert len(assets) > 15
    for asset in assets:
        if not asset.is_file():
            continue
        relative = asset.relative_to(STATIC / "branding")
        group = relative.parts[0]
        if group in {"logos", "icons"}:
            source = ROOT / "docs/branding" / group / "svg" / asset.name
        elif group == "favicons":
            source = ROOT / "docs/branding/favicons" / asset.name
        else:
            source = ROOT / "docs/branding/web" / asset.name
        assert asset.read_bytes() == source.read_bytes(), relative
        response = client.get("/static/" + asset.relative_to(STATIC).as_posix())
        assert response.status_code == 200
        assert response.content == asset.read_bytes()
        if asset.suffix == ".svg":
            document = ElementTree.fromstring(response.content)
            for element in document.iter():
                assert element.tag.rsplit("}", 1)[-1] not in {"script", "foreignObject", "image"}
                for key, value in element.attrib.items():
                    assert not key.lower().startswith("on")
                    assert "url(" not in value
                    if key.rsplit("}", 1)[-1] == "href":
                        assert value.startswith("#")
    assert client.get("/docs/branding/docs/BRAND_GUIDE.md").status_code == 404
    assert client.get("/static/branding/docs/BRAND_GUIDE.md").status_code == 404


def test_local_fonts_are_pinned_licensed_and_served():
    hashes = {
        "Manrope": "3ae11c49db0455a3cc33e37d380f20fdb8c7f8b41dc07625c177e3d87a9d6ae6",
        "Inter": "29160a80ff49ddcab2c97711247e08b1fab27a484a329ce8b813d820dc559031",
    }
    for family, expected in hashes.items():
        data = (STATIC / "fonts" / f"{family}-variable.ttf").read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected
        response = client.get(f"/static/fonts/{family}-variable.ttf")
        assert response.status_code == 200 and response.content == data
        license_text = (STATIC / "fonts" / f"{family}-OFL.txt").read_text(encoding="utf-8")
        assert "SIL OPEN FONT LICENSE" in license_text


def test_branding_is_present_on_every_page_without_external_assets():
    paths = ("/", "/private", "/settings", "/private/workbook/blank", "/private/take-home/blank")
    for path in paths:
        html = client.get(path).text
        assert "brand-mark" not in html and ">FR<" not in html
        assert "goodtogo-horizontal.svg" in html and "goodtogo-symbol-monochrome.svg" in html
        assert "goodtogo-horizontal-dark.svg" in html
        assert 'aria-label="GoodToGo home"' in html
        assert 'rel="apple-touch-icon"' in html and "goodtogo-favicon.svg" in html
        assert "Get your life in order. For the people you love." in html
        for url in re.findall(r'(?:src|href)="([^"]+)"', html):
            if "/static/" in url:
                assert url.startswith("http://testserver/static/")
                assert client.get(url).status_code == 200
    css = (STATIC / "css/app.css").read_text(encoding="utf-8")
    assert "@import" not in css
    assert "https://" not in css and "http://" not in css
    assert "var(--gtg-font-heading)" in css and "var(--gtg-font-body)" in css


def test_stylesheet_versions_and_small_intrinsic_image_sizes():
    html = client.get("/").text
    assert "hero-brand" not in html and "goodtogo-primary.svg" not in html
    assert 'width="130" height="52"' in html
    assert 'width="32" height="32"' in html
    for stylesheet in ("css/app.css", "branding/brand-tokens.css"):
        version = hashlib.sha256((STATIC / stylesheet).read_bytes()).hexdigest()[:12]
        assert f"/static/{stylesheet}?v={version}" in html


def test_dark_logo_has_no_white_panel_and_preserves_geometry():
    light = ElementTree.parse(STATIC / "branding/logos/goodtogo-horizontal.svg").getroot()
    dark = ElementTree.parse(STATIC / "branding/logos/goodtogo-horizontal-dark.svg").getroot()
    assert dark.attrib == light.attrib
    ns = {"svg": "http://www.w3.org/2000/svg"}
    assert [p.attrib["d"] for p in dark.findall(".//svg:path", ns)] == [
        p.attrib["d"] for p in light.findall(".//svg:path", ns)
    ]
    assert dark.find("svg:rect", ns) is None
    assert dark.find("svg:text", ns).attrib["fill"] == "#DCEAF7"
    assert all(element.attrib.get("fill", "").lower() != "#ffffff" for element in dark.iter())
