import re

def is_sql_query_safe(sql_query: str) -> tuple[bool, str]:
    """
    Acts as a deterministic security guardrail. Checks the generated SQL 
    text block for unauthorized destructive keywords before execution.
    """
    if not sql_query:
        return False, "Query is empty."

    # 1. Define a blocklist of destructive SQL commands
    forbidden_keywords = [
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", 
        "TRUNCATE", "REPLACE", "GRANT", "REVOKE"
    ]
    
    # Clean up whitespace and force uppercase to catch sneaky inputs (e.g., "drop table")
    clean_query = sql_query.upper().strip()
    
    # 2. Check for matching forbidden words using regular expressions (word boundaries)
    for keyword in forbidden_keywords:
        # \b ensures we match the exact word "DROP" and not words like "DROP_OFF"
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, clean_query):
            return False, f"Security Violation: Forbidden command '{keyword}' detected in query."
            
    # 3. Structural inspection: Ensure the query actually starts with a safe read command
    if not clean_query.startswith("SELECT") and not clean_query.startswith("WITH"):
        return False, "Security Violation: Query must be a read-only SELECT or WITH statement."
        
    return True, "Query passed all security guardrails."

# Simple self-testing suite
if __name__ == "__main__":
    print("Testing Security Guardrail Node...")
    
    # Test Case A: A safe read query
    safe_query = "SELECT * FROM customers WHERE customer_id = 1;"
    is_safe, msg = is_sql_query_safe(safe_query)
    print(f"\nQuery: {safe_query}\nResult: Safe={is_safe} | Message: {msg}")
    
    # Test Case B: An unsafe write injection query
    unsafe_query = "DROP TABLE customers;"
    is_safe, msg = is_sql_query_safe(unsafe_query)
    print(f"\nQuery: {unsafe_query}\nResult: Safe={is_safe} | Message: {msg}")
