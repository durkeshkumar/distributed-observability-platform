
from typing import Any

from pydantic import BaseModel, Field


class RootCauseIssue(BaseModel):
    type: str
    score: int
    message: str
    span_id: str | None = None
    log_id: int | None = None
    severity: str | None = None
    metric_name: str | None = None
    observed_value: float | None = None
    threshold: float | None = None


class RankedServiceDiagnosis(BaseModel):
    service_name: str
    score: int
    issue_count: int
    issues: list[RootCauseIssue] = Field(default_factory=list)


class RootCauseReportResponse(BaseModel):
    trace_id: str
    most_suspected_service: str | None
    total_issues: int
    ranked_services: list[RankedServiceDiagnosis]
    analysis_status: str
