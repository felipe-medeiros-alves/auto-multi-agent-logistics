from pathlib import Path

from crewai import LLM

from logistics_crew.config import get_openai_api_key, get_openai_model
from logistics_crew.crew import build_shipping_crew
from logistics_crew.reporting.models import ReportSections, RunTrace
from logistics_crew.reporting.render import render_markdown_report
from logistics_crew.shipping.repository import ShippingRepository
from logistics_crew.shipping.tools import ToolTraceCollector


class ConfigurationError(RuntimeError):
    pass


def _sections_from_output(report_task_output) -> ReportSections:
    if report_task_output.pydantic is not None:
        return report_task_output.pydantic  # type: ignore[return-value]
    if report_task_output.json_dict:
        return ReportSections.model_validate(report_task_output.json_dict)
    return ReportSections(
        findings=report_task_output.raw.strip(),
        recommended_actions=[],
        gaps=[],
    )


def run_instruction(
    instruction: str,
    repo: ShippingRepository,
    *,
    verbose: bool = False,
    llm: LLM | None = None,
) -> str:
    if llm is None:
        api_key = get_openai_api_key()
        if not api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        llm = LLM(model=get_openai_model(), api_key=api_key)

    trace = ToolTraceCollector()
    crew = build_shipping_crew(
        repo=repo,
        llm=llm,
        verbose=verbose,
        trace=trace,
    )
    result = crew.kickoff(inputs={"instruction": instruction})
    tasks = result.tasks_output
    plan = tasks[0].raw if tasks else ""
    sections = _sections_from_output(tasks[-1]) if tasks else ReportSections(findings="")
    run_trace = RunTrace(
        instruction=instruction,
        plan=plan,
        tool_events=trace.events,
        findings=sections.findings,
        recommended_actions=sections.recommended_actions,
        gaps=sections.gaps,
    )
    return render_markdown_report(run_trace)


def ensure_database(db_path: Path) -> ShippingRepository:
    from logistics_crew.shipping.seed import init_database

    if not db_path.exists():
        init_database(db_path)
    return ShippingRepository(db_path)
