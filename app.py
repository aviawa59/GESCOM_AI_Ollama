import ollama
from tools import tools
from database_tool import query_database
from gescom_tools import (
    get_meter_count,
    get_division_summary,
    get_division_meter_count
)
import json

# ============================================================
# TOOL FUNCTION MAPPING
# Maps LLM tool names to actual Python functions
# ============================================================

tool_functions = {
    "query_database": query_database,
    "get_meter_count": get_meter_count,
    "get_division_summary": get_division_summary,
    "get_division_meter_count": get_division_meter_count
}

# ============================================================
# LOAD SYSTEM PROMPTS
# ============================================================

with open("prompts/system_prompt.txt","r",encoding="utf-8") as file:
    system_prompt = file.read()


with open("prompts/db_schema_prompt.txt","r",encoding="utf-8") as file:
    db_schema_prompt = file.read()

system_message = system_prompt + "\n\n" + db_schema_prompt

# ============================================================
# APPLICATION HEADER
# ============================================================

print("=" * 60)
print("            GESCOM AI ANALYTICS")
print("AI Assistant for GESCOM Meter replacement Project")
print("=" * 60)

# ============================================================
# CHAT HISTORY
# ============================================================

chat_history = [
    {
        "role": "system",
        "content": system_message
    }
]

# ============================================================
# RETRY CONFIGURATION
# ============================================================

MAX_RETRIES = 2


# ============================================================
# USER INPUT LOOP
# ============================================================

while True:

    user_input = input("Enter your Question: ").strip()

    if user_input.lower() == "exit":
        break

    # --------------------------------------------------------
    # Store user question
    # --------------------------------------------------------

    chat_history.append({
        "role": "user",
        "content": user_input
    })

    # Reset retry counter for every new question
    retry_count = 0


    # ========================================================
    # AGENT LOOP
    # LLM → Tool → Result → LLM

    while True:

        response = ollama.chat(
            model="qwen2.5:7b",
            messages=chat_history,
            tools=tools
        )

        # ====================================================
        # LLM WANTS TO USE A TOOL
        # ====================================================

        if response.message.tool_calls:

            # Store assistant's tool-call message
            chat_history.append(response.message)


            # Process each tool call
            for tool_call in response.message.tool_calls:

                tool_name = tool_call.function.name
                arguments = tool_call.function.arguments


                print(f"\n[Tool Call] {tool_name}")
                print(f"[Arguments] {arguments}")


                # CHECK WHETHER TOOL EXISTS
                if tool_name in tool_functions:

                    tool_function = tool_functions[tool_name]

                    # Execute tool safely
                    try:

                        result = tool_function(**arguments)


                    except Exception as e:

                        result = {
                            "success": False,
                            "error_type": "tool_execution_error",
                            "message": str(e)
                        }


                # UNKNOWN TOOL

                else:

                    result = {
                        "success": False,
                        "error_type": "unknown_tool",
                        "message": f"Unknown tool: {tool_name}"
                    }


                # ------------------------------------------------
                # Display tool result
                # ------------------------------------------------

                print(f"[Tool Result] {result}")

                # ------------------------------------------------
                # Add tool result to chat history
                # ------------------------------------------------

                chat_history.append({
                    "role": "tool",
                    "tool_name": tool_name,
                    "content": json.dumps(result)
                })


                # =================================================
                # TOOL ERROR HANDLING
                # =================================================

                if result.get("success") is False:

                    retry_count += 1

                    print(
                        f"[Tool Error] Retry "
                        f"{retry_count}/{MAX_RETRIES}"
                    )


                    # ------------------------------------------------
                    # Maximum retry limit reached
                    # ------------------------------------------------

                    if retry_count > MAX_RETRIES:

                        print(
                            "\nAI: I was unable to complete "
                            "the requested operation after "
                            "multiple attempts."
                        )

                        break


            # ====================================================
            # EXIT AGENT LOOP IF RETRY LIMIT EXCEEDED
            # ====================================================

            if retry_count > MAX_RETRIES:
                break

            # TOOL RESULT ADDED
            # Send the conversation back to the LLM

            continue

        # ====================================================
        # NO TOOL CALL → FINAL ANSWER
        # ====================================================

        else:

            print("\nAI:", response.message.content)


            chat_history.append({
                "role": "assistant",
                "content": response.message.content
            })


            # End current question
            break