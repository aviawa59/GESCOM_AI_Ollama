tools = [

    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "Execute a read-only SQL query against the GESCOM database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL SELECT query to execute."
                    }
                },
                "required": ["sql"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_meter_count",
            "description": "Get the total number of meters installed in the GESCOM Meter Replacement Project.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_division_summary",
            "description": "Get the total number of installed meters grouped by GESCOM division code.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_division_meter_count",
            "description": "Get the total number of installed meters for a specific GESCOM division code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "division_code": {
                        "type": "string",
                        "description": "GESCOM division code, for example 430005."
                    }
                },
                "required": ["division_code"]
            }
        }
    }

]