from pydantic import BaseModel

from app.content.catalog import CatalogBundle


class TakeHomeResource(BaseModel):
    title: str
    provider: str
    url: str


class TakeHomeTask(BaseModel):
    question_id: str
    section: str
    title: str
    details: str
    priority: str
    needs_professional_help: bool = False
    resources: list[TakeHomeResource]


def build_take_home_tasks(
    catalog: CatalogBundle, answers: dict[str, str]
) -> list[TakeHomeTask]:
    """Create follow-up tasks without mutating or persisting workbook answers."""
    resources_by_id = catalog.resources_by_id
    tasks: list[TakeHomeTask] = []

    for section in catalog.workbook.sections:
        for question in section.questions:
            definition = question.task
            answer = answers.get(question.id)
            if not definition or (
                answer not in definition.when_values and answer != "professional_help"
            ):
                continue
            resources = [
                TakeHomeResource(
                    title=resources_by_id[resource_id].title,
                    provider=resources_by_id[resource_id].provider,
                    url=str(resources_by_id[resource_id].url),
                )
                for resource_id in definition.resource_ids
            ]
            tasks.append(
                TakeHomeTask(
                    question_id=question.id,
                    section=section.title,
                    title=definition.title,
                    details=definition.details,
                    priority=definition.priority,
                    needs_professional_help=answer == "professional_help",
                    resources=resources,
                )
            )

    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    return sorted(tasks, key=lambda task: (priority_order[task.priority], task.title))
