"""
SE Principles MCP Server
========================
FastMCP server that registers all 14 Software Engineering analysis tools.

This is the main entry point for the MCP protocol. Each tool delegates to
its own module in the `tools/` package, following Single Responsibility.
The LLM provider is created once at startup via the Factory pattern and
shared across all tools via Dependency Injection.

Based on principles from:
    - The Pragmatic Programmer (Hunt & Thomas)
    - Clean Code (Robert C. Martin)
    - Code Complete (Steve McConnell)
    - Design Patterns (Gang of Four)
    - Refactoring (Martin Fowler)
    - Designing Data-Intensive Applications (Kleppmann)

Tools:
    1.  analyze_principles     — Full multi-principle audit (30 principles, 5 books)
    2.  detect_code_smells     — 28 code smells from Fowler + Clean Code Ch.17
    3.  suggest_design_pattern — GoF + modern pattern recommendation
    4.  refactor_code          — Principle-compliant refactoring
    5.  generate_boilerplate   — Production-ready pattern templates
    6.  explain_principle      — Deep-dive on any principle from any book
    7.  review_naming          — Clean Code naming audit
    8.  check_solid            — Per-letter SOLID compliance audit
    9.  architecture_review    — System-level design review
    10. complexity_analysis    — Cyclomatic/cognitive complexity analysis
    11. check_error_handling   — Clean Code Ch.7 + Code Complete defensive programming
    12. check_testing          — FIRST principles + developer testing + test smells
    13. pragmatic_review       — The Pragmatic Programmer dedicated audit
    14. check_concurrency      — Thread safety, async patterns, data consistency
"""

from __future__ import annotations

import sys
from typing import Annotated

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load .env file if present (before creating the provider)
load_dotenv()

from se_principles_mcp.llm.factory import create_provider
from se_principles_mcp.tools import (
    analyze_principles,
    detect_code_smells,
    suggest_design_pattern,
    refactor_code,
    generate_boilerplate,
    explain_principle,
    review_naming,
    check_solid,
    architecture_review,
    complexity_analysis,
    check_error_handling,
    check_testing_principles,
    pragmatic_review,
    check_concurrency,
)

# ─── Server Setup ──────────────────────────────────────────────────────────────

mcp = FastMCP(
    "se-principles-mcp",
    instructions=(
        "Software Engineering Principles MCP Server — the most comprehensive SE "
        "quality tool available. 14 tools covering principles from 6 major books: "
        "The Pragmatic Programmer, Clean Code, Code Complete, Design Patterns (GoF), "
        "Refactoring (Fowler), and Designing Data-Intensive Applications. "
        "Analyze, refactor, and generate principle-compliant code."
    ),
)

# Create the LLM provider once at module load
# This will auto-detect from env vars or raise a clear error
try:
    _provider = create_provider()
except (ValueError, ImportError) as e:
    sys.stderr.write(f"⚠️  LLM Provider Error: {e}\n")
    sys.stderr.write("The server will start but tools will fail until configured.\n")
    _provider = None  # type: ignore[assignment]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CORE ANALYSIS TOOLS (1-10)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


# ─── Tool 1: Analyze Principles ───────────────────────────────────────────────

@mcp.tool()
async def analyze_principles_tool(
    code: Annotated[str, "The source code to analyze"],
    language: Annotated[str, "Programming language (e.g., python, typescript, java, go)"],
    context: Annotated[str, "Optional: what the code is supposed to do, to improve accuracy"] = "",
) -> str:
    """Comprehensive analysis of code against 30 SE principles from 5 books: SOLID, DRY, KISS, YAGNI, Clean Code (naming, functions, error handling), Pragmatic Programmer (Orthogonality, Design by Contract, Broken Windows), Code Complete (Defensive Programming, Table-Driven Methods), Law of Demeter, and Separation of Concerns. Returns a 150-point scorecard with severity-ranked violations."""
    return await analyze_principles.run(
        code=code, language=language, context=context, llm=_provider,
    )


# ─── Tool 2: Detect Code Smells ───────────────────────────────────────────────

@mcp.tool()
async def detect_code_smells_tool(
    code: Annotated[str, "The source code to smell-check"],
    language: Annotated[str, "Programming language"],
) -> str:
    """Detect 28 code smells from Fowler's 'Refactoring' and Clean Code Ch.17: Bloaters (Long Method, God Class, Long Parameter List, Data Clumps, Primitive Obsession), OO Abusers (Switch Statements, Refused Bequest, Temporary Field), Change Preventers (Shotgun Surgery, Divergent Change), Dispensables (Dead Code, Speculative Generality, Lazy Class, Duplicate Code, Comments as Deodorant), Couplers (Feature Envy, Inappropriate Intimacy, Message Chains, Middle Man), and Clean Code Heuristics (Boolean Args, Output Args, Flag Args, Obscured Intent). Each smell includes its canonical refactoring technique."""
    return await detect_code_smells.run(
        code=code, language=language, llm=_provider,
    )


# ─── Tool 3: Suggest Design Pattern ───────────────────────────────────────────

@mcp.tool()
async def suggest_design_pattern_tool(
    problem: Annotated[str, "Problem description or existing code that needs a pattern applied"],
    language: Annotated[str, "Target programming language for the implementation example"],
    constraints: Annotated[str, "Optional: any constraints, preferences, or patterns to avoid"] = "",
) -> str:
    """Given a problem description or existing code, recommend the most suitable design pattern(s) from the GoF catalog (23 patterns: Creational, Structural, Behavioral) plus modern patterns. Returns rationale, full implementation example, and trade-offs. Warns against over-engineering."""
    return await suggest_design_pattern.run(
        problem=problem, language=language, constraints=constraints, llm=_provider,
    )


# ─── Tool 4: Refactor Code ────────────────────────────────────────────────────

@mcp.tool()
async def refactor_code_tool(
    code: Annotated[str, "Code to refactor"],
    language: Annotated[str, "Programming language"],
    principles: Annotated[
        list[str] | None,
        "Principles to apply: SOLID, DRY, KISS, YAGNI, CleanCode, LoD, SoC, DesignPatterns. Omit or pass ['all'] for everything."
    ] = None,
    context: Annotated[str, "Optional: what the code does, to avoid changing business logic"] = "",
) -> str:
    """Refactor code to comply with specified SE principles. Preserves all functionality, returns the complete refactored code, and explains every change with the principle it addresses. Applies KISS — won't add unnecessary complexity."""
    return await refactor_code.run(
        code=code, language=language, principles=principles, context=context, llm=_provider,
    )


# ─── Tool 5: Generate Boilerplate ─────────────────────────────────────────────

@mcp.tool()
async def generate_boilerplate_tool(
    pattern: Annotated[str, "Pattern or architecture to generate (e.g., 'Repository Pattern', 'Service Layer with DTOs', 'Observer Pattern', 'CQRS', 'Clean Architecture')"],
    language: Annotated[str, "Target programming language"],
    domain: Annotated[str, "Optional: business domain for meaningful naming (e.g., 'user management', 'order processing')"] = "",
    requirements: Annotated[str, "Optional: specific requirements, variations, or features to include"] = "",
) -> str:
    """Generate production-ready, principle-compliant boilerplate for common patterns and architectures: Repository, Service Layer, Factory, Observer, Strategy, Command, Decorator, CQRS, Event Sourcing, Clean Architecture, Hexagonal, etc. Includes file structure, interfaces, and extension guide."""
    return await generate_boilerplate.run(
        pattern=pattern, language=language, domain=domain, requirements=requirements, llm=_provider,
    )


# ─── Tool 6: Explain Principle ────────────────────────────────────────────────

@mcp.tool()
async def explain_principle_tool(
    principle: Annotated[str, "Principle name (e.g., 'Single Responsibility', 'Open/Closed', 'DRY', 'YAGNI', 'KISS', 'Law of Demeter', 'Composition over Inheritance', 'Fail Fast', 'Orthogonality', 'Design by Contract', 'Broken Windows')"],
    language: Annotated[str, "Preferred language for code examples. Defaults to Python."] = "Python",
    experience_level: Annotated[str, "Adjusts depth: 'junior', 'mid', or 'senior'. Defaults to 'mid'."] = "mid",
) -> str:
    """In-depth explanation of any SE principle from 7 major books (The Pragmatic Programmer, Clean Code, Code Complete, Design Patterns, Refactoring, Mythical Man-Month, Designing Data-Intensive Applications). Includes real-world analogies, good vs bad code examples, common misconceptions, when to apply, when NOT to over-engineer, and related principles."""
    return await explain_principle.run(
        principle=principle, language=language, experience_level=experience_level, llm=_provider,
    )


# ─── Tool 7: Review Naming ────────────────────────────────────────────────────

@mcp.tool()
async def review_naming_tool(
    code: Annotated[str, "Code to review naming in"],
    language: Annotated[str, "Programming language"],
    conventions: Annotated[str, "Naming style convention: camelCase, snake_case, PascalCase, or 'auto-detect' (default)"] = "auto-detect",
) -> str:
    """Audit all identifiers (variables, functions, classes, parameters, constants, files) against Clean Code naming rules: intention-revealing names, no encodings, no noise words, pronounceable names, searchable names, correct boolean prefixes (is/has/can/should). Returns a before/after table plus the revised code."""
    return await review_naming.run(
        code=code, language=language, conventions=conventions, llm=_provider,
    )


# ─── Tool 8: Check SOLID ──────────────────────────────────────────────────────

@mcp.tool()
async def check_solid_tool(
    code: Annotated[str, "Code to audit for SOLID compliance"],
    language: Annotated[str, "Programming language"],
    principles: Annotated[
        list[str] | None,
        "Specific SOLID letters to check: 'S', 'O', 'L', 'I', 'D'. Omit to check all five."
    ] = None,
) -> str:
    """Dedicated SOLID principles audit. Evaluates each letter independently: S — Single Responsibility, O — Open/Closed, L — Liskov Substitution, I — Interface Segregation, D — Dependency Inversion. Returns compliance status, evidence, and fix for each with an overall X/50 score."""
    return await check_solid.run(
        code=code, language=language, principles=principles, llm=_provider,
    )


# ─── Tool 9: Architecture Review ──────────────────────────────────────────────

@mcp.tool()
async def architecture_review_tool(
    description: Annotated[str, "Architecture description, component list, pseudo-diagram, or design document text"],
    architecture_type: Annotated[str, "Architecture style (e.g., monolith, microservices, layered, hexagonal, event-driven, serverless, clean architecture)"] = "unspecified",
    scale: Annotated[str, "Expected scale (e.g., 'startup MVP', '10M users/day', 'enterprise')"] = "unspecified",
) -> str:
    """Review a system architecture against SE best practices: layering, coupling/cohesion, dependency direction, testability, scalability, and common architectural anti-patterns (Big Ball of Mud, Distributed Monolith, God Service, Chatty Services, Shared Database). Provides ASCII diagrams for suggested improvements."""
    return await architecture_review.run(
        description=description, architecture_type=architecture_type, scale=scale, llm=_provider,
    )


# ─── Tool 10: Complexity Analysis ─────────────────────────────────────────────

@mcp.tool()
async def complexity_analysis_tool(
    code: Annotated[str, "Code to analyze for complexity"],
    language: Annotated[str, "Programming language"],
    threshold: Annotated[int, "Cyclomatic complexity threshold above which a function is flagged. Default: 10"] = 10,
) -> str:
    """Measure cyclomatic complexity (decision-point count), cognitive complexity (mental load), nesting depth, function/class size metrics. Flags functions exceeding the threshold and provides concrete decomposition strategies with example extractions."""
    return await complexity_analysis.run(
        code=code, language=language, threshold=threshold, llm=_provider,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DEEP BOOK COVERAGE TOOLS (11-14)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


# ─── Tool 11: Check Error Handling ─────────────────────────────────────────────

@mcp.tool()
async def check_error_handling_tool(
    code: Annotated[str, "The source code to audit for error handling"],
    language: Annotated[str, "Programming language"],
    context: Annotated[str, "Optional: what the code does, for better analysis"] = "",
) -> str:
    """Audit error handling against Clean Code Ch.7 (use exceptions not return codes, don't return null, provide context), Code Complete Ch.8 (defensive programming, assertions, error barricades, graceful degradation), and Pragmatic Programmer (Design by Contract, crash early, assertive programming). Detects 25 error handling rules and 6 anti-patterns (swallowing exceptions, Pokemon exception handling, null cascading, etc.)."""
    return await check_error_handling.run(
        code=code, language=language, context=context, llm=_provider,
    )


# ─── Tool 12: Check Testing Principles ────────────────────────────────────────

@mcp.tool()
async def check_testing_principles_tool(
    code: Annotated[str, "Production source code to analyze testability for"],
    language: Annotated[str, "Programming language"],
    test_code: Annotated[str, "Optional: existing test code to audit alongside the production code"] = "",
    context: Annotated[str, "Optional: what the code does"] = "",
) -> str:
    """Audit testing practices against Clean Code Ch.9 (FIRST: Fast/Independent/Repeatable/Self-validating/Timely, TDD laws), Code Complete Ch.22 (basis testing, boundary analysis, data-flow testing, equivalence partitioning), and Pragmatic Programmer (ruthless testing, find bugs once, property-based testing). Analyzes production code testability (DI, pure functions, seams, global state) and detects 6 test smells (Mystery Guest, Eager Test, Fragile Test, etc.)."""
    return await check_testing_principles.run(
        code=code, language=language, test_code=test_code, context=context, llm=_provider,
    )


# ─── Tool 13: Pragmatic Review ────────────────────────────────────────────────

@mcp.tool()
async def pragmatic_review_tool(
    code: Annotated[str, "The source code to audit"],
    language: Annotated[str, "Programming language"],
    context: Annotated[str, "Optional: what the code does"] = "",
    focus_areas: Annotated[
        list[str] | None,
        "Optional focus areas: 'DRY', 'Orthogonality', 'Design by Contract', 'Broken Windows', 'Reversibility', 'Decoupling', 'Programming by Coincidence'. Omit to check all."
    ] = None,
) -> str:
    """Dedicated audit against The Pragmatic Programmer by Hunt & Thomas. Covers DRY (all 4 types: code, knowledge, data, representational), Orthogonality (module independence), Design by Contract (preconditions, postconditions, invariants), Broken Windows (code decay), Reversibility (vendor lock-in), Decoupling (Law of Demeter), Programming by Coincidence, Tracer Bullets, and Inheritance Tax. Returns orthogonality map, reversibility assessment, broken windows list, and X/80 scorecard."""
    return await pragmatic_review.run(
        code=code, language=language, context=context, focus_areas=focus_areas, llm=_provider,
    )


# ─── Tool 14: Check Concurrency ───────────────────────────────────────────────

@mcp.tool()
async def check_concurrency_tool(
    code: Annotated[str, "The source code to audit for concurrency issues"],
    language: Annotated[str, "Programming language"],
    concurrency_model: Annotated[str, "Concurrency model: 'threads', 'async-await', 'multiprocessing', 'actors', or 'auto-detect' (default)"] = "auto-detect",
    context: Annotated[str, "Optional: what the code does"] = "",
) -> str:
    """Audit concurrent/async code against Clean Code Ch.13 (SRP for concurrency, limit shared data, keep synchronized sections small), common bugs (race conditions, deadlocks, starvation, livelock), async/await anti-patterns (forgotten awaits, blocking in async, task leaks, sequential awaits for independent work), and data consistency principles from Designing Data-Intensive Applications (atomicity, idempotency). Returns shared state map and X/50 concurrency scorecard."""
    return await check_concurrency.run(
        code=code, language=language, concurrency_model=concurrency_model, context=context, llm=_provider,
    )
