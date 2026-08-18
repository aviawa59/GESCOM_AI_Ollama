tools = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "Execute a read-only SQL query against the GESCOM database",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL SELECT query to execute"
                    }
                },
                "required": ["sql"]
            }
        }
    }
]
