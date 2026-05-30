# Resume File Assistant Assignment

This project implements file-system tools for reading, listing, writing, and searching resume documents, then connects those tools to an LLM so user requests can trigger tool calls automatically.

## Project structure

- `fs_tools.py` - Core file tools required in Part A
- `llm_file_assistant.py` - LLM integration for tool calling in Part B
- `requirements.txt` - Python dependencies
- `sample_data/resumes/` - Dummy resume files for testing

## Features

### Part A - Core file system tools
- `read_file(filepath)` reads `.txt`, `.pdf`, and `.docx` resumes
- `list_files(directory, extension=None)` lists files recursively with metadata
- `write_file(filepath, content)` writes files and creates parent directories
- `search_in_file(filepath, keyword)` performs case-insensitive search with surrounding context

### Part B - LLM integration
- Uses OpenAI function calling
- Lets the model choose which file tools to call
- Supports prompts such as:
  - `Read all resumes in the resumes folder`
  - `Find resumes mentioning Python experience`
  - `Create a summary file for resume_john_doe.pdf`

## Setup

1. Create a virtual environment:
   - Windows: `python -m venv venv && venv\\Scripts\\activate`
   - macOS/Linux: `python -m venv venv && source venv/bin/activate`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Add your API key:
   - Create a `.env` file in the project root
   - Add: `OPENAI_API_KEY=your_key_here`
   - Optional: `OPENAI_MODEL=gpt-4o-mini`

## Usage

### Test the file tools directly

```python
from fs_tools import read_file, list_files, search_in_file, write_file

print(list_files('sample_data/resumes', '.pdf'))
print(search_in_file('sample_data/resumes/resume_john_doe.txt', 'Python'))
```

### Run the LLM assistant

```bash
python llm_file_assistant.py
```

Example interaction:
- User: `Find resumes mentioning Python experience`
- Assistant: identifies resume files, searches them, and reports matching candidates.

## How the tool calling works

1. The user sends a natural-language query.
2. The LLM decides whether it needs `list_files`, `read_file`, `search_in_file`, or `write_file`.
3. The Python app executes the selected tool.
4. Tool results are fed back to the LLM.
5. The LLM returns a final answer.

## Dummy data included

The sample folder contains TXT, DOCX, and PDF resumes for different candidates with skills such as Python, Java, Spring Boot, React, AWS, SQL, and machine learning.

## Demo video suggestion

Record a 2-3 minute video covering:
1. Project structure overview
2. Running the assistant
3. Query: `Read all resumes in the resumes folder`
4. Query: `Find resumes mentioning Python experience`
5. Query: `Create a summary file for resume_john_doe.pdf`
6. Show the generated summary file

## Notes

- PDF extraction quality depends on the structure of the PDF.
- DOCX extraction reads paragraph text.
- The project is intentionally simple and easy to extend.
