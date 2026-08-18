import ollama
from tools import tools
from database_tool import query_database
import json

# ============== Calling System Prompts ============== #
with open("prompts/system_prompt.txt", "r", encoding="utf-8") as file:
    system_prompt = file.read()

with open("prompts/db_schema_prompt.txt", "r", encoding="utf-8") as file:
    db_schema_prompt = file.read()

system_message = system_prompt + "\n\n" + db_schema_prompt

print("="*60)
print("            GESCOM AI ANALYTICS")
print("AI Assistant for GESCOM Meter replacement Project")
print("="*60)


# ============== Call History ============== #
chat_history = [
    {
        "role" : "system",
        "content" : system_message
    }
]

# ============== LLM Call & History Tracking  ============== #
while True:
    user_input = input("Enter your Question: ").strip()

    if user_input.strip().lower() == "exit":
        break
    # -- Storing User Messages
    chat_history.append(
        {
            "role" : "user",
            "content" : user_input
        }
    )

    response = ollama.chat(
        model="qwen2.5:7b",
        messages=chat_history,
        tools=tools
    )

    # --------------------------------------------------
    # If the LLM wants to use a tool
    # --------------------------------------------------
    if response.message.tool_calls:

        # Add the assistant's tool-call message to history
        chat_history.append(response.message)

        # Process tool calls
        for tool_call in response.message.tool_calls:

            tool_name = tool_call.function.name
            arguments = tool_call.function.arguments

            print(f"\n[Tool Call] {tool_name}")
            print(f"[Arguments] {arguments}")

            if tool_name == "query_database":

                sql = arguments["sql"]
                result = query_database(sql)

                print(f"[Tool Result] {result}")

                chat_history.append({
                    "role": "tool",
                    "tool_name": tool_name,
                    "content": json.dumps(result)
                })

        # Tool result has been added.
        # Go back to the LLM so it can decide what to do next.
        continue

    # --------------------------------------------------
    # No tool call → final answer
    # --------------------------------------------------

    else:

        print("\nAI:", response.message.content)

        chat_history.append({
            "role": "assistant",
            "content": response.message.content
        })

        break