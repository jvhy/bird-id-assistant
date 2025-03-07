import asyncio

from ollama import AsyncClient

from bird_id_assistant.db import query_vector_db, get_documents


def continue_conversation(*args, **kwargs):
    """Small LLMs are very eager to call a function even when it not required.
    This is a dummy function that the LLM can call instead of making an unnecessary db query.
    """
    return


async def reply_to_user(message_history: list[dict]) -> str:
    client = AsyncClient()

    default_tool = {
        "type": "function",
        "function": {
            "name": "continue_conversation",
            "description": "",
        }
    }

    # Define our search tool
    query_tool = {
        "type": "function",
        "function": {
            "name": "query_vector_db",
            "description": "Queries a vector database of bird species Wiki documents and returns the closest matching one(s). This function should be called very conservatively.",
            "parameters": {
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {
                        "type": "str",
                        "description": "Bird species search query"
                    },
                    "n_results": {
                        "type": "int",
                        "description": "Number of closest matching documents to retrieve from the database"
                    }
                }
            }
        }
    }

    # First, let Ollama decide if it needs to search
    response = await client.chat(
        "llama3.1:8b-instruct-q4_K_M",
        messages=message_history,
        tools=[default_tool, query_tool]
    )

    # Check if Ollama wants to use the search tool
    if response.message.tool_calls:
        for tool in response.message.tool_calls:
            match tool.function.name:
                case "query_vector_db":
                    print("Let me check the database...")
                    tool.function.arguments["n_results"] = int(tool.function.arguments["n_results"])
                    result = get_documents(query_vector_db(**tool.function.arguments))
                    message_history.extend([response.message, {"role": "tool", "name": tool.function.name, "content": str(result)}])
                case "continue_conversation":
                    pass
                case _:
                    pass

        # Get final response from Ollama with the search results
        final_response = await client.chat(
            "llama3.1:8b-instruct-q4_K_M",
            messages=message_history
        )
        return final_response.message.content

    # If no tool is called, return the direct response
    return response.message.content


async def main():
    chat_history = []
    while True:
        question = input("> ")
        chat_history.append({"role": "user", "content": question})
        answer = await reply_to_user(chat_history)
        print(answer + "\n")
        chat_history.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    asyncio.run(main())
