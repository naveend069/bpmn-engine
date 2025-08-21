import json
import uuid
from fastapi import FastAPI, Body
import uvicorn

class WorkflowEngine:
    def __init__(self, process_file):
        with open(process_file, "r") as f:
            self.process = json.load(f)
        self._validate_process()
        self.context = {}

    def _validate_process(self):
        required_keys = ["id", "start", "nodes"]
        for key in required_keys:
            if key not in self.process:
                raise ValueError(f"Missing key in process file: {key}")

    def run_until_pause(self, context, start_node=None):
        self.context.update(context)
        current_node_id = start_node or self.process["start"]

        while True:
            node = self.process["nodes"][current_node_id]
            node_type = node["type"]

            print(f"➡️ Node: {current_node_id} ({node_type})")

            if node_type == "startEvent":
                current_node_id = node.get("next")

            elif node_type == "scriptTask":
                print("   ⚙️ Running script...")
                local_vars = dict(self.context)
                try:
                    exec(node.get("script", ""), {}, local_vars)
                    self.context.update(local_vars)
                except Exception as e:
                    print(f"⚠️ Script error in {node.get('name')}: {e}")
                current_node_id = node.get("next")

            elif node_type == "exclusiveGateway":
                next_node = None
                for cond in node.get("conditions", []):
                    try:
                        result = eval(cond["expression"], {}, self.context)
                        print(f"   ↳ condition '{cond['expression']}' == {result}")
                        if result:
                            next_node = cond["next"]
                            break
                    except Exception as e:
                        print(f"⚠️ Condition error {cond['expression']} ({e})")
                if not next_node:
                    raise Exception(f"No valid condition in gateway {node.get('name')}")
                print(f"   → {next_node}")
                current_node_id = next_node

            elif node_type == "userTask":
                print(f"   👤 User task: {node.get('name')}")
                return "paused", current_node_id, node.get("next")

            elif node_type == "endEvent":
                print(f"✅ Process finished at: {node.get('name')}")
                return "completed", current_node_id, None


def run_cli():
    engine = WorkflowEngine("process.json")
    value = int(input("Enter input value (number): "))
    engine.context["value"] = value

    status, current_node, next_node = engine.run_until_pause(engine.context)

    while status == "paused":
        task = engine.process["nodes"][current_node]["name"].lower()
        if "hr" in task:
            ans = input("HR approval? (y/n): ")
            engine.context["hr_approval"] = ans.lower() == "y"
        elif "supervisor" in task:
            ans = input("Supervisor approval? (y/n): ")
            engine.context["approval"] = ans.lower() == "y"

        status, current_node, next_node = engine.run_until_pause(engine.context, start_node=next_node)

    print(f"Workflow finished with status: {status}")


STORAGE_FILE = "workflow_store.json"

def load_instances():
    try:
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_instances(instances):
    with open(STORAGE_FILE, "w") as f:
        json.dump(instances, f, indent=2)

app = FastAPI()

@app.post("/start-process")
def start_process(data: dict = Body(...)):
    workflow_instances = load_instances()
    input_data = data.get("input", {})
    engine = WorkflowEngine("process.json")
    engine.context.update(input_data)

    status, current_node, next_node = engine.run_until_pause(engine.context)
    instance_id = str(uuid.uuid4())

    workflow_instances[instance_id] = {
        "current_node": current_node,
        "next_node": next_node,
        "context": engine.context,
        "status": status,
    }

    save_instances(workflow_instances)

    return {"workflow_instance_id": instance_id, "current_node": current_node, "status": status}


@app.post("/resume-process/{workflow_instance_id}")
def resume_process(workflow_instance_id: str, approvals: dict = Body(...)):
    workflow_instances = load_instances()
    instance = workflow_instances.get(workflow_instance_id)
    if not instance:
        return {"error": "Workflow instance not found"}

    engine = WorkflowEngine("process.json")
    engine.context.update(instance["context"])
    engine.context.update(approvals)

    current_node = instance["next_node"] or instance["current_node"]
    status, current_node, next_node = engine.run_until_pause(engine.context, start_node=current_node)

    if status != "paused":
        workflow_instances.pop(workflow_instance_id, None)
    else:
        workflow_instances[workflow_instance_id] = {
            "current_node": current_node,
            "next_node": next_node,
            "context": engine.context,
            "status": status,
        }

    save_instances(workflow_instances)

    return {
        "workflow_instance_id": workflow_instance_id,
        "current_node": current_node if status == "paused" else None,
        "status": status,
    }


@app.get("/status/{workflow_instance_id}")
def get_status(workflow_instance_id: str):
    workflow_instances = load_instances()
    instance = workflow_instances.get(workflow_instance_id)
    if not instance:
        return {"error": "Workflow instance not found"}
    return {
        "workflow_instance_id": workflow_instance_id,
        "current_node": instance["current_node"],
        "status": instance["status"],
        "context": instance["context"],
    }




if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "start":
        run_cli()
    else:
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
