import ollama
from tools import tools
from database_tool import query_database
from utility_tools import get_current_datetime
from entity_resolution import resolve_division
import json


# ============================================================
# LOAD SYSTEM PROMPTS
# ============================================================

with open("prompts/system_prompt.txt", "r", encoding="utf-8") as file:
    system_prompt = file.read()

with open("prompts/db_schema_prompt.txt", "r", encoding="utf-8") as file:
    db_schema_prompt = file.read()

system_message = system_prompt + "\n\n" + db_schema_prompt


# ============================================================
# TOOL FUNCTION MAPPING
# Maps LLM tool names to actual Python functions
# ============================================================

tool_functions = {
    "query_database": query_database,
    "get_current_datetime": get_current_datetime,
    "resolve_division": resolve_division
}


# ============================================================
# GROUNDED FINAL ANSWER
# Generates the final answer using ONLY:
# 1. Current user question
# 2. Latest relevant tool result
# ============================================================

def generate_final_answer(user_question, tool_result):

    final_prompt = f"""
You are generating the final answer for the user's current question.

CURRENT USER QUESTION:
{user_question}

LATEST TOOL RESULT:
{json.dumps(tool_result, ensure_ascii=False)}

Instructions:

- Answer ONLY the current user question.
- Use the tool result as the factual source of truth.
- Do not invent or assume any information.
- Do not introduce a date, month, year, division, subdivision,
  section, filter, or other condition that is not supported by
  the current question or tool result.
- If the tool result contains a numerical value, use that exact value.
- If the tool result is zero, clearly report zero.
- Do not use information from previous user questions.
- Do not mention previous questions or previous analysis.
- Do not mention SQL or internal tool processing.
- Do not expose internal reasoning.
- Answer professionally and concisely.
"""

    response = ollama.chat(
        model="qwen2.5:7b",
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": final_prompt
            }
        ]
    )

    return response.message.content


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
MAX_ORCHESTRATION_ATTEMPTS = 2


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


    # --------------------------------------------------------
    # Reset state for every new question
    # --------------------------------------------------------

    retry_count = 0
    orchestration_attempts = 0

    # Tracks whether an entity resolution tool was successfully used
    entity_resolution_used = False

    # Stores the latest successful database result
    latest_database_result = None

    # Stores the latest successful tool result
    latest_tool_result = None


    # ========================================================
    # AGENT LOOP
    #
    # LLM → Tool → Result → LLM
    #
    # The loop continues until:
    # 1. All required tools have been used
    # 2. A database result is available when required
    # 3. The LLM is ready to provide the final answer
    # ========================================================

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


            # ------------------------------------------------
            # Process each tool call
            # ------------------------------------------------

            for tool_call in response.message.tool_calls:

                tool_name = tool_call.function.name
                arguments = tool_call.function.arguments


                print(f"\n[Tool Call] {tool_name}")
                print(f"[Arguments] {arguments}")


                # =================================================
                # CHECK WHETHER TOOL EXISTS
                # =================================================

                if tool_name in tool_functions:

                    tool_function = tool_functions[tool_name]


                    # ------------------------------------------------
                    # Execute tool safely
                    # ------------------------------------------------

                    try:

                        result = tool_function(**arguments)

                    except Exception as e:

                        result = {
                            "success": False,
                            "error_type": "tool_execution_error",
                            "message": str(e)
                        }


                # =================================================
                # UNKNOWN TOOL
                # =================================================

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
                # TRACK SUCCESSFUL TOOL RESULTS
                # =================================================

                if result.get("success") is True:

                    # ------------------------------------------------
                    # Database result
                    # ------------------------------------------------

                    if tool_name == "query_database":

                        latest_database_result = result
                        latest_tool_result = result


                    # ------------------------------------------------
                    # Entity resolution result
                    # ------------------------------------------------

                    elif tool_name == "resolve_division":

                        entity_resolution_used = True
                        latest_tool_result = result


                    # ------------------------------------------------
                    # Other successful tools
                    # ------------------------------------------------

                    else:

                        latest_tool_result = result


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


            # ------------------------------------------------
            # Tool result added.
            #
            # Send the conversation back to the LLM so it can
            # decide whether another tool call is required.
            # ------------------------------------------------

            continue


        # ====================================================
        # NO TOOL CALL
        #
        # The LLM has returned a normal response.
        #
        # Before accepting it as the final answer, check whether
        # entity resolution was performed without database
        # verification.
        # ====================================================

        else:

            # =================================================
            # ORCHESTRATION GUARD
            
            # Entity resolution only identifies an entity.
            # It does NOT answer a database question.

            # If an entity was resolved but no database result
            # exists yet, do NOT allow the LLM to hallucinate
            # a database answer.
            # =================================================

            
            if (
                entity_resolution_used
                and latest_database_result is None
            ):

                orchestration_attempts += 1

                if orchestration_attempts > MAX_ORCHESTRATION_ATTEMPTS:

                    print(
                        "\nAI: I was unable to complete the database "
                        "analysis after multiple attempts."
                    )

                    break

                print(
                    "[Orchestration] Entity resolved successfully, "
                    "but database verification is still required."
                )

                # Get resolved division information
                resolved_code = latest_tool_result.get("division_code")
                resolved_name = latest_tool_result.get("division_name")

                # Explicit continuation instruction for the LLM
                chat_history.append({
                    "role": "user",
                    "content": (
                        f"ENTITY RESOLUTION COMPLETED.\n\n"
                        f"Original user question:\n"
                        f"{user_input}\n\n"
                        f"Resolved Division:\n"
                        f"Name: {resolved_name}\n"
                        f"Code: {resolved_code}\n\n"
                        f"The original question still requires database analysis.\n\n"
                        f"IMPORTANT:\n"
                        f"Preserve the analytical intent of the ORIGINAL question.\n"
                        f"Do not reduce a requested breakdown into a total count.\n\n"
                        f"If the user requested sub-division-wise analysis, "
                        f"the query MUST filter the resolved division and "
                        f"GROUP BY cd.sub_division.\n\n"
                        f"If the user requested section-wise analysis, "
                        f"the query MUST filter the resolved division and "
                        f"GROUP BY cd.section.\n\n"
                        f"If the user requested another grouping level, "
                        f"preserve that requested grouping level.\n\n"
                        f"You MUST now call query_database.\n"
                        f"Do not provide a final answer yet.\n"
                        f"Do not invent or estimate database results."
                    )
                })

                continue

            # =================================================
            # DETERMINE RESULT FOR FINAL ANSWER
            # =================================================

            if latest_database_result is not None:

                final_result = latest_database_result

            else:

                final_result = latest_tool_result


            # =================================================
            # GENERATE GROUNDED FINAL ANSWER
            # =================================================

            if final_result is not None:

                final_answer = generate_final_answer(
                    user_input,
                    final_result
                )

            else:

                # General questions that do not require tools
                # can use the original LLM response.

                final_answer = response.message.content


            # =================================================
            # DISPLAY FINAL ANSWER
            # =================================================

            print("\nAI:", final_answer)

            # =================================================
            # STORE FINAL ANSWER IN CHAT HISTORY

            chat_history.append({
                "role": "assistant",
                "content": final_answer
            })

            # END CURRENT QUESTION
            break