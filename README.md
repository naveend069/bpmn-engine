# BPMN Engine

A lightweight BPMN (Business Process Model and Notation) engine built in Python.  
This engine reads a BPMN-like workflow from a file and executes it step by step, supporting tasks, decisions, and user inputs.

---

## Features

- **Script Tasks** – Execute Python code snippets.
- **Exclusive Gateways** – Conditional branching based on task results.
- **User Input Tasks** – Pause workflow and request input from the user.
- **Start and End Events** – Define clear entry and exit points in your workflow.
- **Easy-to-use** – Load workflows from JSON or YAML-like step definitions.

---

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/bpmn-engine.git
cd bpmn-engine
python -m venv venv
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate

pip install -r requirements.txt

python main.py start
Enter input value (number): 12
➡️ Node: start_event_1 (startEvent)
➡️ Node: script_task_1 (scriptTask)
   ⚙️ Running script...
➡️ Node: gateway_1 (exclusiveGateway)
   ↳ condition 'result > 50' failed
   ↳ condition 'result <= 50' passed
➡️ Node: end_event_1 (endEvent)
Workflow completed!
[
  {
    "id": "start_event_1",
    "type": "startEvent",
    "next": "script_task_1"
  },
  {
    "id": "script_task_1",
    "type": "scriptTask",
    "script": "result = input_value * 5",
    "next": "gateway_1"
  },
  {
    "id": "gateway_1",
    "type": "exclusiveGateway",
    "conditions": [
      {"condition": "result > 50", "next": "end_event_2"},
      {"condition": "result <= 50", "next": "end_event_1"}
    ]
  },
  {
    "id": "end_event_1",
    "type": "endEvent"
  },
  {
    "id": "end_event_2",
    "type": "endEvent"
  }
]
[startEvent] --> [scriptTask] --> [exclusiveGateway]
                                   /        \
                              result>50    result<=50
                               /              \
                         [endEvent2]       [endEvent1]
