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

    def run(self, context):
        self.context = context
        current_node_id = self.process["start"]

        while True:
            node = self.process["nodes"][current_node_id]
            node_type = node["type"]

            print(f"➡️ Node: {current_node_id} ({node_type})")

            if node_type == "startEvent":
                current_node_id = node.get("next")

            elif node_type == "scriptTask":
                print("   ⚙️ Running script...")
                self._run_script(node)
                current_node_id = node.get("next")

            elif node_type == "exclusiveGateway":
                next_node = None
                for cond in node.get("conditions", []):
                    try:
                        if eval(cond["expression"], {}, self.context):
                            print(f"   ↳ condition '{cond['expression']}' == True → {cond['next']}")
                            next_node = cond["next"]
                            break
                        else:
                            print(f"   ↳ condition '{cond['expression']}' == False")
                    except Exception as e:
                        print(f"   ⚠️ Condition error: {cond['expression']} ({e})")
                if not next_node:
                    raise Exception("No valid condition in gateway")
                current_node_id = next_node

            elif node_type == "userTask":
                print(f"   👤 User task: {node.get('name')}")
                # Pause for approval
                if "hr" in node.get("name", "").lower():
                    ans = input("HR approval? (y/n): ")
                    self.context["hr_approval"] = ans.lower() == "y"
                elif "supervisor" in node.get("name", "").lower():
                    ans = input("Supervisor approval? (y/n): ")
                    self.context["approval"] = ans.lower() == "y"
                current_node_id = node.get("next")

            elif node_type == "endEvent":
                print(f"✅ Process finished at: {node.get('name')}")
                return "finished"

    def _run_script(self, node):
        try:
            local_vars = dict(self.context)
            exec(node.get("script", ""), {}, local_vars)
            self.context.update(local_vars)
        except Exception as e:
            print(f"   ⚠️ Script error in node {node.get('name')}: {e}")
