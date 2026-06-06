"""
Deployment and task text processing utilities.

This module provides helper functions for summarizing deployment activity
and preparing ClickUp task textual representations for NLP-based processing.

It is primarily used to generate lightweight structured signals for LLMs
and to support semantic comparison between tasks and external data sources
such as GitHub commits or deployment events.

Main responsibilities:
- Summarize deployment activity into compact analytical signals
- Build normalized textual representations of ClickUp tasks for vectorization

Functions:
    summarize_deployments: Generate a structured summary of deployment activity
        including environment breakdown, success/failure counts, and recency signals.
"""

from datetime import datetime


def summarize_deployments(deployments: list, date_closed: datetime | None) -> dict:
    """
    Summarize deployment activity into lightweight signals for LLM consumption.
    """
    if not deployments:
        return {
            "total": 0,
            "summary": "No deployments found.",
        }

    prod_deployments = [
        d for d in deployments
        if "prod" in (d.environment or "").lower()
    ]
    staging_deployments = [
        d for d in deployments
        if "staging" in (d.environment or "").lower()
    ]

    successful_prod = [d for d in prod_deployments if d.state == "success"]
    failed_prod = [d for d in prod_deployments if d.state == "failure"]

    latest_prod = max(
        (d for d in successful_prod if d.created_at),
        key=lambda d: d.created_at,
        default=None
    )

    prod_after_close = [
        d for d in successful_prod
        if date_closed and d.created_at and d.created_at >= date_closed
    ]

    return {
        "total": len(deployments),
        "prod_successful": len(successful_prod),
        "prod_failed": len(failed_prod),
        "staging_count": len(staging_deployments),
        "prod_deployments_after_close": len(prod_after_close),
        "latest_prod_deployment": str(latest_prod.created_at.date()) if latest_prod else None,
        "summary": (
            f"{len(successful_prod)} successful prod deployment(s), "
            f"last on {latest_prod.created_at.date() if latest_prod else 'N/A'}. "
            f"{len(failed_prod)} failed. "
            f"{len(staging_deployments)} staging deployment(s)."
        )
    }
