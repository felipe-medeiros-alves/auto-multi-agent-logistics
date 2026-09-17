from pydantic import BaseModel, Field


class ToolEvent(BaseModel):
    name: str
    args: dict[str, object]
    result: str


class RunTrace(BaseModel):
    instruction: str
    plan: str = ""
    tool_events: list[ToolEvent] = Field(default_factory=list)
    findings: str = ""
    recommended_actions: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)


class ReportSections(BaseModel):
    findings: str
    recommended_actions: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
