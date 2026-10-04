from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, HttpUrl, model_validator


class ResourceLink(BaseModel):
    id: str
    provider: str
    title: str
    url: HttpUrl
    purpose: Literal["prepare", "survivor", "reference"]
    jurisdiction: str = "US"
    last_verified: str
    summary: str


class FollowUpTaskDefinition(BaseModel):
    when_values: list[str] = Field(min_length=1)
    title: str
    details: str
    priority: Literal["critical", "high", "medium", "low"]
    resource_ids: list[str] = Field(default_factory=list)


class Question(BaseModel):
    id: str
    prompt: str
    help_text: str
    response_type: Literal["readiness"] = "readiness"
    sensitivity: Literal["standard", "sensitive", "highly_sensitive"] = "sensitive"
    recommended_review_months: int = Field(default=12, ge=1, le=60)
    task: FollowUpTaskDefinition | None = None


class Section(BaseModel):
    id: str
    title: str
    description: str
    estimated_minutes: int = Field(ge=1, le=60)
    questions: list[Question] = Field(min_length=1)


class WorkbookCatalog(BaseModel):
    id: str
    version: str
    title: str
    jurisdiction: str
    last_reviewed: str
    disclaimer: str
    sections: list[Section] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_ids(self) -> "WorkbookCatalog":
        section_ids = [section.id for section in self.sections]
        question_ids = [question.id for section in self.sections for question in section.questions]
        if len(section_ids) != len(set(section_ids)):
            raise ValueError("section IDs must be unique")
        if len(question_ids) != len(set(question_ids)):
            raise ValueError("question IDs must be unique")
        return self


class CatalogBundle(BaseModel):
    workbook: WorkbookCatalog
    resources: list[ResourceLink]

    @model_validator(mode="after")
    def valid_resource_references(self) -> "CatalogBundle":
        resource_ids = {resource.id for resource in self.resources}
        referenced_ids = {
            resource_id
            for section in self.workbook.sections
            for question in section.questions
            if question.task
            for resource_id in question.task.resource_ids
        }
        missing = referenced_ids - resource_ids
        if missing:
            raise ValueError(f"unknown resource IDs: {sorted(missing)}")
        return self

    @property
    def resources_by_id(self) -> dict[str, ResourceLink]:
        return {resource.id: resource for resource in self.resources}


def _load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected a mapping in {path}")
    return value


@lru_cache
def load_catalog() -> CatalogBundle:
    root = Path(__file__).resolve().parent / "core_us"
    workbook = WorkbookCatalog.model_validate(_load_yaml(root / "workbook.yaml"))
    resources_document = _load_yaml(root / "digital_guides.yaml")
    resources = [ResourceLink.model_validate(item) for item in resources_document["resources"]]
    return CatalogBundle(workbook=workbook, resources=resources)
