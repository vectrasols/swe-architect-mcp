from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from swe_architect_mcp.llm.base import LLMProvider
from swe_architect_mcp.tools import (
    advance_lifecycle_phase,
    generate_lifecycle_diagram,
    review_lifecycle_gate,
    start_product_build,
    summarize_project_state,
)


class FakeProvider(LLMProvider):
    @property
    def provider_name(self) -> str:
        return "Fake"

    @property
    def model_name(self) -> str:
        return "fake-model"

    async def generate(self, system_prompt: str, user_message: str) -> str:
        if "Return only Mermaid syntax" in system_prompt:
            return "flowchart TD\n    A[Idea] --> B[Product]"
        if "quality gate reviewer" in system_prompt:
            return "# Lifecycle Gate Review\n\n## Status\npass"
        return ""


def _project_id_from(result: str) -> str:
    match = re.search(r"Project id: `([^`]+)`", result)
    assert match is not None
    return match.group(1)


class LifecycleToolTests(unittest.IsolatedAsyncioTestCase):
    def test_old_principle_tools_are_not_registered_in_active_server(self) -> None:
        server_source = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "swe_architect_mcp"
            / "server.py"
        ).read_text(encoding="utf-8")

        self.assertIn("start_product_build_tool", server_source)
        self.assertNotIn("analyze_principles_tool", server_source)
        self.assertNotIn("detect_code_smells_tool", server_source)
        self.assertNotIn("check_solid_tool", server_source)

    async def test_start_product_build_creates_workspace_when_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = await start_product_build.run(
                idea="Build me a task management app",
                workspace_root=tmp,
                target_users="students",
                constraints="Python MVP",
                allow_workspace_write=True,
                allow_diagrams=True,
                llm=FakeProvider(),
            )

            project_id = _project_id_from(result)
            project_dir = Path(tmp) / ".se-lifecycle" / project_id
            self.assertTrue(project_dir.exists())
            self.assertTrue((project_dir / "state.json").exists())
            self.assertTrue((project_dir / "00_vision.md").exists())
            self.assertTrue((project_dir / "decision_log.md").exists())
            self.assertIn("communication", result)

    async def test_start_product_build_does_not_write_without_permission(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            await start_product_build.run(
                idea="Build me a notes app",
                workspace_root=tmp,
                allow_workspace_write=False,
                allow_diagrams=True,
                llm=None,
            )

            self.assertFalse((Path(tmp) / ".se-lifecycle").exists())

    async def test_lifecycle_cannot_skip_without_override_rationale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            start = await start_product_build.run(
                idea="Build me a booking system",
                workspace_root=tmp,
                allow_workspace_write=True,
                allow_diagrams=True,
                llm=None,
            )
            project_id = _project_id_from(start)

            result = await advance_lifecycle_phase.run(
                project_id=project_id,
                workspace_root=tmp,
                phase_override="construction",
                user_response="",
                allow_workspace_write=True,
                allow_diagrams=True,
                llm=None,
            )

            self.assertIn("Status: `blocked`", result)
            self.assertIn("skip lifecycle", result)

    async def test_requirements_artifact_has_required_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            start = await start_product_build.run(
                idea="Build me a library catalog",
                workspace_root=tmp,
                allow_workspace_write=True,
                allow_diagrams=True,
                llm=None,
            )
            project_id = _project_id_from(start)

            result = await advance_lifecycle_phase.run(
                project_id=project_id,
                workspace_root=tmp,
                user_response="Users are librarians and students.",
                allow_workspace_write=False,
                allow_diagrams=True,
                llm=None,
            )

            self.assertIn("Functional Requirements", result)
            self.assertIn("Non-Functional Requirements", result)
            self.assertIn("Domain Requirements", result)
            self.assertIn("Inverse Requirements", result)
            self.assertIn("Design Constraints", result)
            self.assertIn("Acceptance Criteria", result)

    async def test_mermaid_diagram_is_saved_when_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            start = await start_product_build.run(
                idea="Build me an inventory system",
                workspace_root=tmp,
                allow_workspace_write=True,
                allow_diagrams=True,
                llm=None,
            )
            project_id = _project_id_from(start)

            result = await generate_lifecycle_diagram.run(
                project_id=project_id,
                workspace_root=tmp,
                diagram_type="architecture",
                source_artifact="# Inventory System",
                allow_workspace_write=True,
                llm=FakeProvider(),
            )

            diagram_path = (
                Path(tmp)
                / ".se-lifecycle"
                / project_id
                / "diagrams"
                / "architecture.mmd"
            )
            self.assertTrue(diagram_path.exists())
            self.assertIn("flowchart", diagram_path.read_text(encoding="utf-8"))
            self.assertIn("```mermaid", result)

    async def test_gate_review_statuses(self) -> None:
        strong = """# Requirements

## Functional Requirements
FR-1 primary workflow.

## Non-Functional Requirements
Security, reliability, usability, and performance.

## Domain Requirements
Domain data and rules.

## Inverse Requirements
Do not build out-of-scope work.

## Design Constraints
Use the agreed stack.

## Acceptance Criteria
The user can complete the primary workflow.

## Priority
Must, should, could.
"""
        weak = "TBD"

        pass_result = await review_lifecycle_gate.run(
            project_id="p",
            workspace_root=".",
            phase="requirements",
            artifact_text=strong,
            changed_files=[],
            strictness="balanced",
            allow_workspace_write=False,
            llm=None,
        )
        blocked_result = await review_lifecycle_gate.run(
            project_id="p",
            workspace_root=".",
            phase="requirements",
            artifact_text=weak,
            changed_files=[],
            strictness="balanced",
            allow_workspace_write=False,
            llm=None,
        )

        self.assertIn("pass", pass_result)
        self.assertIn("blocked", blocked_result)

    async def test_traceability_and_resume_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            start = await start_product_build.run(
                idea="Build me a CRM",
                workspace_root=tmp,
                allow_workspace_write=True,
                allow_diagrams=True,
                llm=None,
            )
            project_id = _project_id_from(start)

            await advance_lifecycle_phase.run(
                project_id=project_id,
                workspace_root=tmp,
                user_response="Sales team MVP.",
                allow_workspace_write=True,
                allow_diagrams=True,
                llm=None,
            )
            await advance_lifecycle_phase.run(
                project_id=project_id,
                workspace_root=tmp,
                user_response="Proceed to modeling.",
                allow_workspace_write=True,
                allow_diagrams=True,
                llm=None,
            )

            matrix = (
                Path(tmp)
                / ".se-lifecycle"
                / project_id
                / "traceability_matrix.md"
            ).read_text(encoding="utf-8")
            summary = await summarize_project_state.run(
                project_id=project_id,
                workspace_root=tmp,
            )

            self.assertIn("FR-1", matrix)
            self.assertIn("Primary workflow", matrix)
            self.assertIn("Current phase: `modeling`", summary)


if __name__ == "__main__":
    unittest.main()
