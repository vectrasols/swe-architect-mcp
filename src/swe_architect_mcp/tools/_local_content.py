"""Deterministic product-context helpers for no-API fallback content."""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class LocalProductContext:
    """Small inferred context used when no LLM provider is configured."""

    product_name: str
    actor_label: str
    primary_entity: str
    secondary_entity: str
    workflow: str
    stack_hint: str
    constraints_summary: str


DOMAIN_HINTS: tuple[tuple[tuple[str, ...], tuple[str, str, str]], ...] = (
    (
        ("pharmacy", "medicine", "medication", "inventory", "stock"),
        (
            "InventoryItem",
            "StockMovement",
            "record items, update stock levels, and flag low inventory",
        ),
    ),
    (
        ("task", "todo", "kanban", "project"),
        ("Task", "Project", "create tasks, update status, and track completion"),
    ),
    (
        ("ticket", "support", "helpdesk", "issue"),
        ("Ticket", "Agent", "create tickets, assign owners, and resolve issues"),
    ),
    (
        ("booking", "reservation", "appointment", "schedule"),
        ("Booking", "AvailabilitySlot", "request, confirm, and manage bookings"),
    ),
    (
        ("library", "catalog", "book", "loan"),
        ("Book", "Loan", "search catalog records and manage item availability"),
    ),
    (
        ("crm", "sales", "lead", "customer", "opportunity"),
        ("Lead", "Opportunity", "capture leads, track contacts, and move deals forward"),
    ),
    (
        ("note", "notes", "notebook"),
        ("Note", "Notebook", "create notes, organize them, and retrieve saved content"),
    ),
    (
        ("order", "shop", "store", "ecommerce", "cart"),
        ("Order", "Product", "browse products, place orders, and track fulfillment"),
    ),
    (
        ("invoice", "billing", "payment", "finance"),
        ("Invoice", "Payment", "create invoices, record payments, and track balances"),
    ),
    (
        ("student", "course", "school", "class"),
        ("Student", "Course", "manage learners, courses, and progress records"),
    ),
)


def infer_product_context(
    *,
    idea: str,
    target_users: str = "",
    constraints: str = "",
    user_response: str = "",
) -> LocalProductContext:
    """Infer stable product names and nouns for fallback artifacts."""
    combined = " ".join(
        part for part in (idea, target_users, constraints, user_response) if part
    )
    lower = combined.lower()
    primary_entity = "DomainRecord"
    secondary_entity = "WorkflowEvent"
    workflow = "capture a request, validate it, save the result, and show feedback"

    for keywords, values in DOMAIN_HINTS:
        if any(keyword in lower for keyword in keywords):
            primary_entity, secondary_entity, workflow = values
            break

    return LocalProductContext(
        product_name=product_name_from_text(idea or combined or "Product"),
        actor_label=_actor_label(target_users, user_response),
        primary_entity=primary_entity,
        secondary_entity=secondary_entity,
        workflow=workflow,
        stack_hint=_stack_hint(constraints, user_response),
        constraints_summary=constraints or "No fixed constraints have been confirmed yet.",
    )


def product_name_from_text(text: str) -> str:
    """Return a readable product title from an idea or artifact heading."""
    idea_match = re.search(r"^Idea:\s*(.+)$", text, flags=re.IGNORECASE | re.MULTILINE)
    heading = _first_markdown_heading(text)
    value = (
        idea_match.group(1)
        if idea_match
        else heading or (text.strip().splitlines()[0] if text.strip() else "Product")
    )
    value = re.sub(
        r"^(build|create|make|develop)\s+(me\s+)?(a|an|the)?\s*",
        "",
        value.strip(),
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\b(app|application|system|platform|tool|software|product)\b",
        "",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value).strip()
    if not value:
        return "Product"
    return " ".join(word.capitalize() for word in value.split()[:6])


def mermaid_label(value: str) -> str:
    """Sanitize a label for simple Mermaid node text."""
    cleaned = re.sub(r"[\[\]{}|<>`]", "", value).strip()
    return cleaned or "Product"


def mermaid_id(value: str, fallback: str = "Node") -> str:
    """Create a simple Mermaid-safe identifier."""
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", value)
    return cleaned or fallback


def _first_markdown_heading(text: str) -> str:
    """Extract the first Markdown heading from text."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""


def _actor_label(target_users: str, user_response: str) -> str:
    """Pick a useful actor label from supplied context."""
    text = target_users.strip() or user_response.strip()
    if not text:
        return "Primary User"
    text = re.sub(r"^(users are|user is|target users are)\s+", "", text, flags=re.I)
    text = re.split(r"[.;\n]", text, maxsplit=1)[0]
    text = re.sub(r"\s+", " ", text).strip()
    return text[:60] or "Primary User"


def _stack_hint(constraints: str, user_response: str) -> str:
    """Pick a short stack/constraint hint from known context."""
    text = " ".join(part for part in (constraints, user_response) if part)
    if not text.strip():
        return "Use the simplest stack that fits the user's workspace."
    lowered = text.lower()
    for keyword in (
        "python",
        "django",
        "fastapi",
        "flask",
        "react",
        "next",
        "node",
        "sqlite",
        "postgres",
        "local",
        "desktop",
        "web",
    ):
        if keyword in lowered:
            return f"Honor the confirmed {keyword} constraint or preference."
    return "Honor the supplied constraints before choosing implementation details."
