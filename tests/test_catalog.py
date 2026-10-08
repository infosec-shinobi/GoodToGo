from app.content.catalog import load_catalog


def test_catalog_is_complete_and_references_are_valid():
    catalog = load_catalog()
    questions = [
        question
        for section in catalog.workbook.sections
        for question in section.questions
    ]

    assert len(catalog.workbook.sections) >= 6
    assert len(questions) >= 18
    assert catalog.workbook.version == "0.1.2"
    assert catalog.workbook.jurisdiction == "US-OH"
    assert catalog.resources
    assert all(section.estimated_minutes > 0 for section in catalog.workbook.sections)
    assert any(question.response_type == "applicability" for question in questions)
    assert any(question.applies_when for question in questions)


def test_guide_links_are_https_and_have_review_dates():
    catalog = load_catalog()

    for resource in catalog.resources:
        assert str(resource.url).startswith("https://")
        assert resource.last_verified
