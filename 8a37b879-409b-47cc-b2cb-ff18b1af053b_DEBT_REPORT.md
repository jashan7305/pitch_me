# Debt Report - 8a37b879-409b-47cc-b2cb-ff18b1af053b

## /backend/main.py
- Debt Score: 10/100
- Observations: Missing type hints, basic structure, not currently testable due to missing dependencies.
- Refactor suggestions: Add type hints for all functions, modularize route definitions.

## /backend/api/routes.py
- Debt Score: 80/100
- Observations: Extremely high cognitive complexity, long function (generate), no type hints, heavy external dependencies, hardcoded paths, mixed responsibilities.
- Refactor suggestions: Extract PDF processing, RAG orchestration, and API response generation into separate service classes. Introduce Pydantic models for request/response validation.

## /backend/agent/audit_agent.py
- Debt Score: 70/100
- Observations: Depends on `google-genai` which is not available in the sandbox. Logic is tightly coupled to Gemini API.
- Refactor suggestions: Introduce an abstraction layer for LLM interactions.

## /backend/agent/company_agent.py
- Debt Score: 60/100
- Observations: Depends on external AI libraries.
- Refactor suggestions: Standardize interface for agent interactions.

## /backend/agent/gemini_client.py
- Debt Score: 50/100
- Observations: Depends on `google-genai`.
- Refactor suggestions: Abstract the underlying client.

## /backend/agent/pitch_agent.py
- Debt Score: 60/100
- Observations: Logic depends on external AI libraries.
- Refactor suggestions: Similar to audit_agent.py.

## /backend/models/pitch.py
- Debt Score: 30/100
- Observations: Simple Pydantic models, could benefit from more detailed field descriptions.
- Refactor suggestions: Add field constraints and descriptions.

## /backend/models/policy.py
- Debt Score: 30/100
- Observations: Similar to pitch.py.
- Refactor suggestions: Add field descriptions.

## /backend/models/audit.py
- Debt Score: 40/100
- Observations: Simple Pydantic model.
- Refactor suggestions: Add field descriptions.

## /backend/models/company.py
- Debt Score: 40/100
- Observations: Simple Pydantic model.
- Refactor suggestions: Add field descriptions.

## /backend/service/audit_report.py
- Debt Score: 60/100
- Observations: Hardcoded logic for report generation.
- Refactor suggestions: Use templating engine.

## /backend/service/pitch_generator.py
- Debt Score: 70/100
- Observations: Deeply coupled to RAG and LLM components.
- Refactor suggestions: Decouple generation logic.

## /backend/rag/chunking.py
- Debt Score: 50/100
- Observations: PDF processing logic.
- Refactor suggestions: Use standard library or lightweight tools.

## /backend/rag/extraction.py
- Debt Score: 50/100
- Observations: Text extraction logic.
- Refactor suggestions: Abstract text extraction.

## /backend/rag/retrieval.py
- Debt Score: 60/100
- Observations: RAG orchestration.
- Refactor suggestions: Simplify retrieval logic.

## /backend/rag/build_baselines.py
- Debt Score: 50/100
- Observations: Baseline generation scripts.
- Refactor suggestions: None.

## /backend/rag/embeddings.py
- Debt Score: 50/100
- Observations: Embedding generation.
- Refactor suggestions: Standardize embedding provider.

## /backend/rag/index.py
- Debt Score: 50/100
- Observations: Vector store wrapper.
- Refactor suggestions: None.

## /frontend/js/*.js
- Debt Score: 70/100
- Observations: Direct DOM manipulation, no state management.
- Refactor suggestions: Modernize with a component-based approach.

Note: Python files were not testable because the sandbox environment lacks required third-party dependencies such as `google-genai`, `faiss-cpu`, `pymupdf`, `python-pptx`, etc.
