tools = [

    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": (
                "Execute a read-only SQL SELECT query against the "
                "GESCOM database. Use this for GESCOM analytics, "
                "including counts, summaries, filters, date analysis, "
                "division, sub-division, section, meter type, contractor, "
                "and other database-related questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": (
                            "A valid read-only SQL SELECT query "
                            "using only the tables and columns "
                            "provided in the database schema."
                        )
                    }
                },
                "required": ["sql"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": (
                "Get the current local date and time from the Python "
                "runtime. Use this when the user refers to today, "
                "yesterday, current date, current time, or another "
                "relative date/time that requires the current date. "
                "This tool does not provide GESCOM database information."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type" : "function",
        "function" : {
            "name" : "resolve_division",
            "description" : (
                    "Resolve a GESCOM division name or division code "
                    "to the official division code and division name. "
                    "Use this when the user refers to a specific division "
                    "by name or code."
                ),
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "division" : {
                        "type" : "string",
                        "description" : "Division Name or Division Code provided by the users"
                    }
                },
                "required" : ["division"]
            }
        }
    } 

]