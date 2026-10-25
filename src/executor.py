import sqlite3
import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load configuration variables
load_dotenv()
DB_PATH = os.getenv("DATABASE_PATH", "data/ecommerce.db")

# Initialize official Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def execute_sql_query(sql_query: str) -> tuple[bool, list, list]:
    """
    Executes the validated SQL query against the SQLite instance.
    Returns: (success_status, columns_list, records_list/error_message)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        columns = [description[0] for description in cursor.description] if cursor.description else []
        records = cursor.fetchall()
        
        conn.close()
        return True, columns, records
    except sqlite3.Error as e:
        return False, [], str(e)

def automatic_error_correction_loop(broken_sql: str, error_message: str) -> str:
    """
    Acts as the Error Fixer/Parser node. Feeds SQL syntax errors 
    back into the LLM to get a self-healed, corrected execution string.
    """
    print(f"⚠️ Execution failure detected. Activating Error Correction Loop...")
    print(f"   Broken SQL: {broken_sql}")
    print(f"   DB Error: {error_message}")
    
    repair_prompt = f"""
    You are an expert enterprise Database Engineer troubleshooting an execution failure.
    
    The application run this invalid SQLite query:
    {broken_sql}
    
    The database threw this column or syntax error:
    {error_message}
    
    CRITICAL RULES:
    1. Fix the error. Note that the real column name for order amount in our 'orders' table is 'total_amount'.
    2. Output ONLY a raw valid JSON block matching the template below.
    3. Do NOT use markdown code blocks like ```json.

    REQUIRED JSON FORMAT:
    {{
        "repaired_sql": "SELECT ... your clean corrected string here"
    }}
    """
    
    try:
        # Update model value on line 51 to ensure the repair loop matches
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": repair_prompt}],
            temperature=0.0
        )

        
        raw_content = response.choices[0].message.content.strip()
        result = json.loads(raw_content)
        return result.get("repaired_sql", "")
    except Exception as e:
        print(f"❌ Healing loop failure: {str(e)}")
        return ""

if __name__ == "__main__":
    print("\n--- Testing Route 1: Safe Query Execution Success ---")
    valid_query = "SELECT * FROM customers LIMIT 1;"
    success, cols, rows = execute_sql_query(valid_query)
    print(f"Success: {success} | Columns: {cols} | Data: {rows}")
    
    print("\n--- Testing Route 2: Self-Healing Correction Loop ---")
    # Intentional typo: 'customer_amt' column does not exist
    bad_query = "SELECT SUM(customer_amt) FROM orders;"
    success, cols, err_msg = execute_sql_query(bad_query)
    
    if not success:
        fixed_query = automatic_error_correction_loop(bad_query, err_msg)
        print(f"\n✨ Repaired Query Output:\n   {fixed_query}")
