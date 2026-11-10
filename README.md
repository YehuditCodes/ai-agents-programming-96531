# AI Agents Programming (96531.1.1) - Semester A

Course assignments. Each assignment is in its own folder and runs on its own.

| Folder | Assignment |
|--------|------------|
| [`assignment_1/`](assignment_1/) | Stage 1 - investment assistant as a simple, non-agentic program (preferences -> rule-based stock selection -> LLM explanations) |
| [`assignment_2/`](assignment_2/) | Stage 2 - the same flow as a linear LangGraph agent, with a diagram of the agent and test scenarios (`tests_2.docx`) |

## Setup

```bash
pip install -r assignment_2/requirements.txt
```

Create a `.env` file in the repository root (it is not included in the repository):

```
OPENAI_API_KEY=your-key-here
```

## Run

```bash
python assignment_1/stage1.py
python assignment_2/stage2_agent.py
```

See the README in each folder for details.
