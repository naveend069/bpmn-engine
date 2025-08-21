from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from engine import WorkflowEngine
import uuid

app = FastAPI(title="BPMN Workflow Engine API")

workflows = {}  # workflow_id -> workflow state

class StartProcessInput(BaseModel):
    value: int

class ResumeProcessInput(BaseModel):
    hr_approval: bool = None
    approval: bool = None

def run_until_pause(engine: WorkflowEngine, context: dict):
    current_node_id = context.get("current_node", engine.process["start"])
    while True:
        node = engine.process["nodes"][current_node_id]
        node_type = node["type"]

        if node_type == "startEvent":
            current_node_id = node.get("next")

        elif node_type == "scriptTask":
            engine._run_script(node)
            current_node_id = node.get("next")

        elif node_type == "exclusiveGateway":
            next_node = None
            for cond in node.get("conditions", []):
                if eval(cond["expression"], {}, engine.context):
                    next_node = cond["next"]
                    break
            if not next_node:
                raise Exception("No valid condition in gateway")
            current_node_id = next_node

        elif node_type == "userTask":
            context["current_node"] = current_node_id
            return "paused", current_node_id

        elif node_type == "endEvent":
            return "finished", current_node_id

@app.post("/start-process")
def start_process(input_data: StartProcessInput):
    workflow_id = str(uuid.uuid4())
    engine = WorkflowEngine("process.json")
    engine.context = {"value": input_data.value}
    status, current_node = run_until_pause(engine, {"current_node": None})
    workflows[workflow_id] = {
        "engine": engine,
        "context": engine.context,
        "status": status,
        "current_node": current_node
    }
    return {"workflow_id": workflow_id, "status": status, "current_node": current_node}

@app.post("/resume-process/{workflow_id}")
def resume_process(workflow_id: str, resume_data: ResumeProcessInput):
    workflow = workflows.get(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if resume_data.hr_approval is not None:
        workflow["context"]["hr_approval"] = resume_data.hr_approval
    if resume_data.approval is not None:
        workflow["context"]["approval"] = resume_data.approval

    engine = workflow["engine"]
    status, current_node = run_until_pause(engine, workflow["context"])
    workflow.update({
        "status": status,
        "current_node": current_node,
        "context": engine.context
    })
    return {"workflow_id": workflow_id, "status": status, "current_node": current_node}

@app.get("/status/{workflow_id}")
def get_status(workflow_id: str):
    workflow = workflows.get(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {
        "workflow_id": workflow_id,
        "status": workflow["status"],
        "current_node": workflow["current_node"],
        "context": workflow["context"]
    }
    