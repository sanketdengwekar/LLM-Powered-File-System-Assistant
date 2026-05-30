from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from fs_tools import list_files, read_file, search_in_file, write_file

load_dotenv()

SYSTEM_PROMPT = """
You are a file assistant that helps users work with resume documents.
Decide when to use tools based on the user's request.
Use tools to inspect files, search inside resumes, and write summaries.
When a user asks for summaries, create a concise file with the extracted details.
""".strip()

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory, optionally filtered by extension.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string"},
                    "extension": {"type": ["string", "null"]}
                },
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a TXT, PDF, or DOCX file and extract text plus metadata.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_in_file",
            "description": "Search for a keyword in a file and return case-insensitive matches with surrounding context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"},
                    "keyword": {"type": "string"}
                },
                "required": ["filepath", "keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file and create directories if they do not exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["filepath", "content"]
            }
        }
    }
]


def call_tool(name: str, arguments: dict[str, Any]) -> Any:
    tool_map = {
        'list_files': list_files,
        'read_file': read_file,
        'search_in_file': search_in_file,
        'write_file': write_file,
    }
    return tool_map[name](**arguments)


def run_assistant(user_query: str) -> str:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY is not set. Add it to your environment or .env file.')

    client = OpenAI(api_key=api_key)
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    for _ in range(6):
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            messages=messages,
            tools=TOOLS,
            tool_choice='auto',
            temperature=0.2,
        )
        message = response.choices[0].message

        if not message.tool_calls:
            return message.content or ''

        messages.append(message.model_dump())

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            result = call_tool(tool_name, arguments)
            messages.append({
                'role': 'tool',
                'tool_call_id': tool_call.id,
                'name': tool_name,
                'content': json.dumps(result, ensure_ascii=False)
            })

    return 'Tool-calling loop limit reached. Please refine the query.'


if __name__ == '__main__':
    print('Resume File Assistant')
    print("Type 'exit' to quit. Example: Find resumes mentioning Python experience")
    while True:
        query = input('\nYou: ').strip()
        if query.lower() in {'exit', 'quit'}:
            break
        try:
            answer = run_assistant(query)
            print(f'Assistant: {answer}')
        except Exception as exc:
            print(f'Error: {exc}')
