import json

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
        """
        Executes workflow until a userTask is reached or endEvent.
        Returns: status ("paused"/"completed") and current node
        """
        self.context.update(context)
        current_node_id = start_node or self.process["start"]

        while True:
            node = self.process["nodes"][current_node_id]
            node_type = node["type"]

            if node_type == "startEvent":
                current_node_id = node.get("next")

            elif node_type == "scriptTask":
                local_vars = dict(self.context)
                try:
                    exec(node.get("script", ""), {}, local_vars)
                    self.context.update(local_vars)
                except Exception as e:
                    print(f"⚠️ Script error in node {node.get('name')}: {e}")
                current_node_id = node.get("next")

            elif node_type == "exclusiveGateway":
                next_node = None
                for cond in node.get("conditions", []):
                    try:
                        if eval(cond["expression"], {}, self.context):
                            next_node = cond["next"]
                            break
                    except Exception as e:
                        print(f"⚠️ Condition error: {cond['expression']} ({e})")
                if not next_node:
                    raise Exception(f"No valid condition in gateway {node.get('name')}")
                current_node_id = next_node

            elif node_type == "userTask":
                # Pause at userTask
                return "paused", current_node_id

            elif node_type == "endEvent":
                return "completed", current_node_id
