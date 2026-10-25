import os
import json
from groq import Groq
from dotenv import load_dotenv
from src.retriever import get_all_schema_metadata, get_dynamic_few_shots

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_and_route_query(user_query: str) -> dict:
    """Core routing engine enhanced with Dynamic Few-Shot Learning and stable response parsing."""
    schema_context = get_all_schema_metadata()
    few_shot_context = get_dynamic_few_shots(user_query)
    
    system_prompt = f"""
    You are an expert enterprise Data Engineering Text-to-SQL Agent.
    Your job is to analyze a user's natural language query using the provided database schema.

    {schema_context}
    {few_shot_context}

    CRITICAL RULES:
    1. Evaluate if the query is ambiguous, missing critical filters, or impossible to answer with the given schema.
    2. If it is ambiguous, set "is_ambiguous" to true, and write a clear, helpful "clarification_message". Do not write SQL.
    3. If it is clear, set "is_ambiguous" to false, execute a step-by-step reasoning thought process, and write the valid SQLite query.
    4. Never use risky, dangerous modifying commands like DROP, DELETE, UPDATE, INSERT, or ALTER.
    5. Return your response ONLY as a clean, raw valid JSON object matching the template below. 
    6. Do NOT wrap your output in markdown formatting syntax like ```json ... ```. Output raw text braces only.

    REQUIRED JSON OUTPUT FORMAT:
    {{
        "is_ambiguous": true,
        "clarification_message": "Your text question here if ambiguous, otherwise empty string",
        "reasoning": "Step-by-step logic of how you chose tables/columns",
        "generated_sql": "The clean SQLite string here if clear, otherwise empty string"
    }}
    """

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.1
        )
        
        # FIXED: Added array indexing [0] to extract accurately from the gpt-oss token array response
        raw_content = response.choices[0].message.content.strip()
        result = json.loads(raw_content)
        return result
    except Exception as e:
        return {"is_ambiguous": False, "clarification_message": "", "reasoning": str(e), "generated_sql": ""}
