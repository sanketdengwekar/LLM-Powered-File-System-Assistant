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
    query = user_query.lower()

    if "read all resumes" in query:
        files = list_files("sample_data/resumes")
        result = []

        for file in files:
            data = read_file(file["path"])
            result.append(f"\n=== {file['name']} ===\n")
            result.append(data.get("content", "")[:1000])

        return "\n".join(result)

    elif "python experience" in query:
        files = list_files("sample_data/resumes")
        matches = []

        for file in files:
            res = search_in_file(file["path"], "python")
            if res.get("matches"):
                matches.append(file["name"])

        return "Matching resumes:\n" + "\n".join(matches)

    elif "summary" in query:
        files = list_files("sample_data/resumes")

        if not files:
            return "No resumes found"

        resume = files[0]
        content = read_file(resume["path"]).get("content", "")

        summary = content[:500]

        write_file(
            "output/resume_summary.txt",
            summary
        )

        return "Summary saved to output/resume_summary.txt"

    return "Unsupported query."

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
