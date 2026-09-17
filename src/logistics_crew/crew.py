from crewai import Agent, Crew, LLM, Process, Task

from logistics_crew.reporting.models import ReportSections
from logistics_crew.shipping.repository import ShippingRepository
from logistics_crew.shipping.tools import ToolTraceCollector, build_shipping_tools


def build_shipping_crew(
    repo: ShippingRepository,
    llm: LLM,
    *,
    verbose: bool = False,
    trace: ToolTraceCollector | None = None,
) -> Crew:
    tools = build_shipping_tools(repo, trace=trace)

    planner = Agent(
        role="Logistics planner",
        goal="Turn natural language shipping requests into a clear, ordered plan.",
        backstory=(
            "You break down shipping questions into steps without calling tools. "
            "You only plan read-only lookups (rates, tracking, listing shipments)."
        ),
        llm=llm,
        verbose=verbose,
        allow_delegation=False,
    )

    analyst = Agent(
        role="Shipping analyst",
        goal="Execute the plan using only the provided read-only shipping tools.",
        backstory=(
            "You gather facts from mock shipping data. You never invent tracking IDs "
            "or rates; you always use tools."
        ),
        llm=llm,
        tools=tools,
        verbose=verbose,
        allow_delegation=False,
    )

    reporter = Agent(
        role="Execution reporter",
        goal="Summarize findings and hypothetical next actions for a read-only run.",
        backstory=(
            "You write concise logistics reports. Recommended actions are hypothetical "
            "because this system cannot create labels or mutate shipments."
        ),
        llm=llm,
        verbose=verbose,
        allow_delegation=False,
    )

    plan_task = Task(
        description=(
            "Given the user instruction: {instruction}\n"
            "Produce a numbered plan of read-only steps (which tools to call and why). "
            "Do not call tools yourself."
        ),
        expected_output="Numbered plan with 2-6 steps.",
        agent=planner,
    )

    analyze_task = Task(
        description=(
            "Follow the plan from context and call shipping tools as needed to answer: "
            "{instruction}\n"
            "Capture exact tool results in your notes."
        ),
        expected_output="Bullet list of factual findings backed by tool output.",
        agent=analyst,
        context=[plan_task],
        tools=tools,
    )

    report_task = Task(
        description=(
            "Using the plan and analyst notes in context, produce structured report "
            "sections for instruction: {instruction}"
        ),
        expected_output=(
            "Structured sections: findings (markdown string), recommended_actions "
            "(list of strings, hypothetical only), gaps (list of strings)."
        ),
        agent=reporter,
        context=[plan_task, analyze_task],
        output_pydantic=ReportSections,
    )

    return Crew(
        agents=[planner, analyst, reporter],
        tasks=[plan_task, analyze_task, report_task],
        process=Process.sequential,
        verbose=verbose,
    )
