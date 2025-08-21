# tests/test_gateway.py
import json
from engine import WorkflowEngine

def load_process():
    return {
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

def test_gt_10(tmp_path):
    engine = WorkflowEngine(load_process(), state_file=tmp_path / "state.json")
    result = engine.run({"value": 11})
    assert result == "paused"
    assert engine.current_node == "user_task_a"

def test_leq_10(tmp_path):
    engine = WorkflowEngine(load_process(), state_file=tmp_path / "state.json")
    result = engine.run({"value": 10})
    assert result == "paused"
    assert engine.current_node == "user_task_b"
