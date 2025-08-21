# test_engine.py
import json
from engine import WorkflowEngine

process = {
    "id": "sample_process",
    "start": "start_event_1",
    "nodes": {
        "start_event_1": {"type": "startEvent", "next": "script_task_1"},
        "script_task_1": {"type": "scriptTask", "script": "result = input['value']", "next": "gateway_1"},
        "gateway_1": {
            "type": "exclusiveGateway",
            "conditions": [
                {"expression": "result > 10", "next": "user_task_a"},
                {"expression": "result <= 10", "next": "user_task_b"}
            ]
        },
        "user_task_a": {"type": "userTask", "name": "Approve Request", "next": "end_event_1"},
        "user_task_b": {"type": "userTask", "name": "Manual Review", "next": "end_event_2"},
        "end_event_1": {"type": "endEvent"},
        "end_event_2": {"type": "endEvent"}
    }
}

def test_gateway_high_value(tmp_path):
    engine = WorkflowEngine(process, state_file=tmp_path / "state.json")
    result = engine.run({"value": 15})
    assert result == "paused"
    assert engine.current_node == "user_task_a"

def test_gateway_low_value(tmp_path):
    engine = WorkflowEngine(process, state_file=tmp_path / "state.json")
    result = engine.run({"value": 5})
    assert result == "paused"
    assert engine.current_node == "user_task_b"

def test_resume_process(tmp_path):
    engine = WorkflowEngine(process, state_file=tmp_path / "state.json")
    # Start with value 20 → goes to user_task_a and pauses
    engine.run({"value": 20})
    assert engine.current_node == "user_task_a"

    # Load state and resume → must finish at end_event_1
    engine.load_state()
    result = engine.run(resume=True)
    assert result == "finished"
