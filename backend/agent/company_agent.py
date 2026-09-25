from __future__ import annotations

import os

import serpapi

from agent.gemini_client import create_client, generate_content_with_retry
from models.company import CompanyProfile

from config import GEMINI_API_KEY, SERPAPI_API_KEY, GEMINI_GENERATION_MODEL


COMPANY_RESEARCH_QUERIES = [
    "{company} company overview industry operations",
    "{company} employees workforce size",
    "{company} annual report operations locations risks",
    "{company} employee benefits healthcare",
]

def _search_company(
    company_name: str,
) -> list[dict[str, str]]:
    """
    Search public web sources for insurance-relevant
    information about a company.
    """

    client = serpapi.Client(api_key=SERPAPI_API_KEY)

    results: list[dict[str, str]] = []

    for query_template in COMPANY_RESEARCH_QUERIES:
        query = query_template.format(
            company=company_name
        )

        response = client.search(
            {
                "engine": "google",
                "q": query,
            }
        )

        results.append(
            {
                "query": query,
                "results": _extract_search_results(response),
            }
        )

    return results


def _extract_search_results(response) -> str:
    """
    Convert a SerpAPI response into plain text that can be
    passed to Gemini.

    We intentionally keep this generic instead of depending
    on a provider-specific result structure.
    """

    sections: list[str] = []

    # Organic search results
    organic_results = response.get(
        "organic_results",
        [],
    )

    for result in organic_results:
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        link = result.get("link", "")

        sections.append(
            f"Title: {title}\n"
            f"Snippet: {snippet}\n"
            f"URL: {link}"
        )

    # Knowledge graph, when available
    knowledge_graph = response.get(
        "knowledge_graph"
    )

    if knowledge_graph:
        title = knowledge_graph.get(
            "title",
            "",
        )

        description = knowledge_graph.get(
            "description",
            "",
        )

        if title or description:
            sections.append(
                f"Knowledge Graph:\n"
                f"Title: {title}\n"
                f"Description: {description}"
            )

    if not sections:
        return "No useful search results were returned."

    return "\n\n".join(sections)


def _build_research_context(
    search_results: list[dict[str, str]],
) -> str:
    """
    Convert search results into a context block for Gemini.
    """

    sections: list[str] = []

    for result in search_results:
        sections.append(
            f"""
SEARCH QUERY:
{result["query"]}

SEARCH RESULTS:
{result["results"]}
""".strip()
        )

    return "\n\n".join(sections)


def build_company_profile(
    company_name: str,
) -> CompanyProfile:
    """
    Research a company and convert the findings into a
    structured CompanyProfile.
    """

    company_name = company_name.strip()

    if not company_name:
        raise ValueError(
            "Company name cannot be empty"
        )

    search_results = _search_company(
        company_name
    )

    research_context = _build_research_context(
        search_results
    )

    client = create_client()

    prompt = f"""
You are preparing a company profile for a corporate
health-insurance marketing pitch.

Company:
{company_name}

Use ONLY the supplied search results as factual evidence.

Your task is to create a structured company profile that
identifies information relevant to employee health-insurance
needs.

IMPORTANT RULES:

1. Do not invent company facts.
2. Do not assume an employee count if one is not supported.
3. If a fact is uncertain, leave the corresponding field
   null or use an empty list.
4. Separate publicly supported facts from inferred
   insurance exposures.
5. Every insurance exposure must include:
   - exposure
   - rationale
   - evidence
   - confidence
6. The evidence field must describe the actual public fact
   that led to the exposure.
7. Do not claim that the company currently has a particular
   insurance policy unless the supplied sources explicitly
   establish it.
8. Do not recommend a policy.
9. Keep the output concise and relevant to corporate
   employee health insurance.

SUPPLIED SEARCH RESULTS:

{research_context}
"""

    response = generate_content_with_retry(
        client=client,
        model=GEMINI_GENERATION_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": CompanyProfile,
        },
    )

    return CompanyProfile.model_validate_json(
        response.text
    )