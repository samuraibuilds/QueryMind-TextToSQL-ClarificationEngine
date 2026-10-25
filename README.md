# QueryMind — Autonomous Text-to-SQL Compiler & Intent-Disambiguation Engine

**Transform natural language into secure, optimized SQL queries with intelligent clarification and automated error recovery.**

QueryMind is a modular Text-to-SQL orchestration system that converts natural-language business questions into executable SQL queries. It combines large language models, schema-aware query generation, programmatic security guardrails, ambiguity detection, dynamic few-shot retrieval, and automated query repair in a unified data engineering pipeline.

The goal is to make database analytics more accessible while maintaining control over query execution, schema interpretation, and runtime failures.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Example Use Cases](#example-use-cases)
- [Installation and Setup](#installation-and-setup)
- [Environment Configuration](#environment-configuration)
- [Database Initialization](#database-initialization)
- [Running QueryMind](#running-querymind)
- [Security and Reliability](#security-and-reliability)
- [Project Structure](#project-structure)
- [Future Enhancements](#future-enhancements)

---

## Overview

Traditional database querying requires users to understand SQL syntax, database schemas, table relationships, and aggregation logic.

QueryMind addresses this challenge by translating business questions into SQL through a controlled orchestration pipeline.

| Capability | Description |
|---|---|
| Natural Language to SQL | Converts business questions into SQL queries using an LLM. |
| Schema-Aware Generation | Uses database schema information to guide table selection, joins, and column references. |
| Intent Disambiguation | Detects ambiguous requests and asks for clarification before query execution. |
| SQL Security Guardrails | Rejects prohibited SQL operations before execution. |
| Dynamic Few-Shot Retrieval | Supplies relevant, approved SQL examples to improve query generation. |
| Automated Query Repair | Uses database errors to guide corrective query-generation attempts. |
| Relational Query Execution | Executes validated queries against a configured relational database. |
| Structured Result Reporting | Returns query results in a readable tabular format. |

## Key Features

### 1. Intelligent Intent Disambiguation

Business questions often lack sufficient information to identify the correct data source or metric.

For example:

> "Show me the records from last month."

The system may need to distinguish between transaction dates, customer registration dates, and other temporal fields.

QueryMind should detect unresolved ambiguity and request additional information before generating or executing a query.

**Expected behavior:**
- Identify competing interpretations of a request.
- Detect missing entities, metrics, or date fields.
- Generate a focused clarification question.
- Resume processing after receiving the required information.

### 2. Zero-Trust SQL Security

QueryMind uses programmatic SQL validation to enforce execution policies rather than relying exclusively on model instructions.

| Security Control | Purpose |
|---|---|
| Statement Validation | Checks generated SQL before execution. |
| Destructive Operation Blocking | Rejects prohibited operations such as `DROP`, `DELETE`, and `UPDATE` when operating in read-only analytics mode. |
| Read-Only Database Access | Restricts database permissions to reduce the impact of unauthorized queries. |
| Query Execution Controls | Prevents invalid or disallowed statements from reaching the database. |
| Error Isolation | Keeps runtime errors within the controlled recovery pipeline. |

**Important:** Regex-based keyword checks alone are not a complete SQL security boundary. Production deployments should also use SQL parsing, read-only database credentials, statement restrictions, and execution limits.

### 3. Dynamic Few-Shot Context Provisioning

QueryMind can retrieve relevant, engineering-approved SQL examples based on the incoming business question.

These examples, referred to as *Golden Queries*, provide contextual guidance for query generation.

| Stage | Operation |
|---|---|
| 1 | Receive the natural-language question. |
| 2 | Analyze its intent and relevant schema entities. |
| 3 | Retrieve matching approved SQL examples. |
| 4 | Inject selected examples into the generation context. |
| 5 | Generate and validate the SQL query. |

This approach can improve consistency across repeated analytical patterns and reduce unnecessary prompt context.

### 4. Automated Query Repair

Database execution may fail because of schema changes, invalid column names, incorrect joins, or SQL syntax errors.

QueryMind can use controlled retries to correct eligible failures.

1. Generate a candidate SQL query.
2. Validate the query against security policies.
3. Execute the query against the database.
4. Capture a sanitized error message if execution fails.
5. Provide the error and relevant schema information to the repair process.
6. Regenerate and revalidate the query.
7. Retry within a predefined limit or return a clear failure message.

The recovery mechanism should never bypass security validation, and retries should be bounded to prevent infinite loops and excessive API usage.

---

## System Architecture

```text
Natural Language Business Question
                |
                v
       Intent Classification
                |
                v
      Ambiguity Detection
          /         \
         /           \
  Ambiguous        Unambiguous
      |                  |
      v                  v
Clarification       Schema Retrieval
      |                  |
      v                  v
User Response      Golden Query Retrieval
      |                  |
      +--------+---------+
               |
               v
        SQL Generation
               |
               v
       Security Validation
               |
               v
        Query Execution
           /       \
          /         \
      Success      Failure
         |             |
         v             v
    Return Results  Bounded Repair
                         |
                         v
                  Revalidate SQL
                         |
                         v
                  Retry or Fail
```
## Architecture Reference

The following diagram is a reference architecture for the QueryMind Text-to-SQL Agent, illustrating the intended workflow for semantic caching, intent disambiguation, schema retrieval, SQL generation, security validation, query execution, and error recovery.

[Text-to-SQL Agent Architecture](assets/text-to-sql.png)

**Reference:** Architecture diagram sourced from YouTube. Credit the original creator and link to the original video here: [YouTube video link](https://www.youtube.com/watch?v=phxEKe3ngK0).

*Note: This diagram is used as an architectural reference. It does not necessarily represent the exact implementation currently present in this repository.*

## Technology Stack

| Technology | Role |
|---|---|
| Python | Core orchestration and application logic |
| SQL | Relational data querying and aggregation |
| SQLite | Local analytical database |
| Groq API | Access to an LLM for SQL generation and correction, when configured |
| Retrieval Component | Retrieves relevant approved SQL examples |
| Environment Variables | Stores configuration and API credentials outside source code |
| Git and GitHub | Version control and project documentation |

*The final technology list should reflect the actual packages and integrations implemented in the repository.*

---

## Example Use Cases

### Scenario A: Revenue Analysis

**Business question**

> What is the total revenue generated by electronics category sales?

**Illustrative SQL query**

```sql
SELECT
    SUM(o.payment_value) AS total_revenue
FROM orders AS o
JOIN products AS p
    ON o.product_id = p.product_id
WHERE LOWER(p.product_category_name) = 'electronics';
```

**Expected processing flow**

| Stage | Result |
|---|---|
| Intent Analysis | Identify a revenue aggregation and product-category filter. |
| Schema Mapping | Resolve the relevant transaction and product tables. |
| SQL Generation | Generate a query with an appropriate join and aggregation. |
| Security Validation | Check the statement against execution policies. |
| Query Execution | Execute the validated query against the database. |
| Result Reporting | Return the calculated revenue. |

**Illustrative output**

| total_revenue |
|---:|
| 1215.50 |

*The result is an example only. Actual values depend on the database contents, schema, join relationships, and revenue definition.*

### Scenario B: Ambiguous Date-Based Request

**Business question**

> Show me the records from last month.

**Clarification response**

> Which records would you like to see from last month: orders created during that period, customers registered during that period, or another type of record?

| Detected Issue | Required Action |
|---|---|
| Missing target entity | Identify the table or business entity. |
| Ambiguous temporal field | Determine which date column defines the period. |
| Undefined output scope | Clarify which records or fields should be returned. |

QueryMind should pause execution until the required context is available rather than selecting a table or date field arbitrarily.

---

## Installation and Setup

### Prerequisites

- Python 3.10 or a compatible version supported by the project's dependencies.
- Git.
- A valid Groq API key if the application uses the Groq API.
- The project repository and any required dataset files.

### 1. Clone the Repository

Replace the placeholder URL with the actual GitHub repository URL.

```bash
git clone <YOUR_REPOSITORY_URL>
cd QueryMind-TextToSQL-ClarificationEngine
```

### 2. Create a Virtual Environment

**Windows — PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Ensure that `requirements.txt` exists and contains the dependencies required by the application.

---

## Environment Configuration

Create a `.env` file in the project root directory.

```dotenv
GROQ_API_KEY=your_groq_api_key_here
DATABASE_PATH=data/ecommerce.db
```

| Variable | Purpose |
|---|---|
| `GROQ_API_KEY` | Authenticates requests to the Groq API. |
| `DATABASE_PATH` | Specifies the location of the SQLite database. |

**Security recommendations**

- Never commit `.env` to GitHub.
- Add `.env` and other secret files to `.gitignore`.
- Provide a `.env.example` file containing placeholder values.
- Load environment variables through a configuration library such as `python-dotenv`, if used by the project.
- Rotate credentials immediately if they are accidentally exposed.

Example `.gitignore` entries:

```gitignore
.env
.venv/
__pycache__/
*.py[cod]
data/*.db
```

Adjust the database ignore rule if the repository intentionally includes a small, non-sensitive sample database.

---

## Database Initialization

If the repository contains a database bootstrap script, initialize the database using:

```bash
python setup_db.py
```

The setup script should create the required tables and, where configured, load the sample e-commerce dataset.

Verify that the database file exists at the configured `DATABASE_PATH` and that its tables and relationships match the schema expected by the application.

---

## Running QueryMind

Start the application from the project root:

```bash
python main.py
```

Enter a natural-language business question when prompted.

Example questions:

```text
What is the total revenue from electronics?
```

```text
Which products generated the highest revenue?
```

```text
How many orders were placed last month?
```

```text
Show me the records from last month.
```

The final question should trigger clarification if the application cannot determine the intended entity and date field reliably.

---

## Security and Reliability

QueryMind is designed around a validate-before-execute workflow.

| Risk | Recommended Mitigation |
|---|---|
| Destructive SQL | SQL parsing, explicit statement allowlisting, and read-only database permissions |
| Incorrect table selection | Schema-aware validation and ambiguity detection |
| Invalid SQL generation | Bounded correction and retry logic |
| Schema drift | Refresh schema metadata and validate referenced tables and columns |
| Excessive query execution | Query timeouts, row limits, and resource restrictions |
| API credential exposure | Environment variables and secret management |
| Repeated repair failures | Maximum retry count and structured failure reporting |
| Prompt injection | Treat user input and retrieved examples as untrusted data; enforce security outside the LLM |

These controls should be verified through automated tests before describing the system as production-ready.

---

## Project Structure

A possible repository layout is shown below. Adapt the names to match the files that actually exist in your implementation.

```text
QueryMind-TextToSQL-ClarificationEngine/
│
├── main.py                 # Application entry point
├── setup_db.py             # Database initialization and seeding
├── requirements.txt        # Python dependencies
├── .env.example            # Environment configuration template
├── .gitignore              # Files excluded from version control
├── README.md               # Project documentation
│
├── data/
│   └── ecommerce.db        # Local SQLite database (if generated)
│
├── src/
│   ├── intent.py           # Intent analysis and ambiguity detection
│   ├── schema.py           # Schema inspection and metadata retrieval
│   ├── sql_generator.py    # SQL generation
│   ├── guardrails.py       # SQL validation and security controls
│   ├── retriever.py        # Golden Query retrieval
│   ├── executor.py         # Database query execution
│   └── repair.py           # Bounded SQL correction and retries
│
└── tests/
    ├── test_guardrails.py
    ├── test_intent.py
    └── test_sql_generation.py
```

---

## Future Enhancements

- Semantic schema retrieval for large databases.
- More robust SQL parsing and policy enforcement.
- Support for PostgreSQL and other relational database engines.
- Automated evaluation using a benchmark of natural-language questions and expected SQL results.
- Query execution plans and performance optimization.
- Observability through structured logs, metrics, and tracing.
- Human approval for sensitive or expensive queries.
- Regression tests for schema changes and query repair.
- Role-based access controls and per-user query permissions.

---

## Engineering Philosophy

QueryMind treats Text-to-SQL as a controlled compilation workflow rather than a single LLM prompt.

Its central design principle is:

**Understand the intent → Resolve ambiguity → Ground the schema → Generate SQL → Validate security → Execute → Recover safely.**

The objective is to build a system that makes natural-language analytics more accessible without sacrificing database integrity, predictable execution, or operational control.

---



