BPMN Engine

A lightweight BPMN workflow engine built in Python that reads a JSON workflow definition, executes steps, handles decisions, pauses for user input, and supports resuming via API.

Note: In my first test case, I completed the project successfully using CLI (command line interface).
As an optional feature, I also integrated and tested the project via API using FastAPI.

Features

Executes script tasks (Python snippets) safely

Conditional branching via exclusive gateways

Pauses at user tasks until confirmation

Tracks and resumes workflow state

Simple HTTP API for remote workflow execution

Prerequisites

Python 3.10+

Pip

Install dependencies:

pip install fastapi uvicorn pydantic

Workflow JSON Structure

Example process.json:

{
  "id": "sample_process",
  "start": "start_event_1",
  "nodes": {
    "start_event_1": {"type": "startEvent","name":"Process Started","next":"script_task_1"},
    "script_task_1": {"type": "scriptTask","name":"Employee Work Evaluation","script":"result = value * 2","next":"gateway_1"},
    "gateway_1": {"type": "exclusiveGateway","name":"Performance Check","conditions":[
        {"expression": "result > 50", "next": "user_task_supervisor"},
        {"expression": "result > 10", "next": "user_task_hr"},
        {"expression": "True", "next": "end_event_fail"}]},
    "user_task_supervisor": {"type": "userTask","name":"Supervisor Approval","next":"gateway_2"},
    "gateway_2": {"type": "exclusiveGateway","name":"Supervisor Decision","conditions":[
        {"expression": "approval == True","next":"end_event_success"},
        {"expression": "True","next":"end_event_fail"}]},
    "user_task_hr": {"type": "userTask","name":"HR Final Review","next":"gateway_3"},
    "gateway_3": {"type": "exclusiveGateway","name":"HR Decision","conditions":[
        {"expression": "hr_approval == True","next":"end_event_success"},
        {"expression": "True","next":"end_event_fail"}]},
    "end_event_success": {"type": "endEvent","name":"Process Completed Successfully"},
    "end_event_fail": {"type": "endEvent","name":"Process Failed / Rejected"}
  }
}

CLI Usage

Run workflow from the command line:

python main.py start

Example Run:
➡️ Node: start_event_1 (startEvent)
➡️ Node: script_task_1 (scriptTask)
   ⚙️ Running script...
➡️ Node: gateway_1 (exclusiveGateway)
   ↳ condition 'result > 50' == False
   ↳ condition 'result > 10' == True → user_task_hr
➡️ Node: user_task_hr (userTask)
   👤 User task: HR Final Review
HR approval? (y/n): y
➡️ Node: gateway_3 (exclusiveGateway)
   ↳ condition 'hr_approval == True' == True → end_event_success
➡️ Node: end_event_success (endEvent)
✅ Process finished at: Process Completed Successfully


Explanation:

Starts at start_event_1.

Runs script_task_1 (evaluates result = value * 2).

Gateway gateway_1 evaluates conditions and chooses the correct path.

Pauses at user_task_hr until user input (y/n).

Continues through gateway_3 and ends at end_event_success.
# FastAPI-Workflow

A FastAPI-based workflow engine with a simple and intuitive API.

API Usage

Start the FastAPI server:

uvicorn main:app --reload
open postman or thunder client and test the endpoints

Endpoints
Start a Workflow
POST /start-process
Content-Type: application/json

{
  "workflow_id": "sample_process",
  "input": {"value": 12}
}


Response:

{
  "workflow_instance_id": "abc123",
  "current_node": "user_task_hr",
  "status": "paused"
}

Resume a Paused Workflow
POST /resume-process/abc123
body

{
  "hr_approval": true,
  "approval": true
}


Response:

{
  "workflow_instance_id": "abc123",
  "current_node": "end_event_success",
  "status": "completed"
}

Check Workflow Status
GET /status/abc123


Response:

{
  "workflow_instance_id": "abc123",
  "current_node": "user_task_hr",
  "status": "paused",
  "context": {
      "value": 12,
      "result": 24,
      "hr_approval": true
  }
}
