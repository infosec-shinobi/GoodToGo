from app.content.catalog import load_catalog
from app.services.tasks import build_take_home_tasks


def test_ready_and_not_applicable_answers_do_not_create_tasks():
    catalog = load_catalog()
    answers = {
        question.id: "complete" if index % 2 else "not_applicable"
        for index, question in enumerate(
            question
            for section in catalog.workbook.sections
            for question in section.questions
        )
    }

    assert build_take_home_tasks(catalog, answers) == []


def test_unready_answers_create_priority_sorted_tasks_with_guides():
    catalog = load_catalog()
    answers = {
        question.id: "not_started"
        for section in catalog.workbook.sections
        for question in section.questions
    }

    tasks = build_take_home_tasks(catalog, answers)
    priority = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    assert tasks
    assert [priority[task.priority] for task in tasks] == sorted(
        priority[task.priority] for task in tasks
    )
    assert any(task.resources for task in tasks)
    assert all(resource.url.startswith("https://") for task in tasks for resource in task.resources)

