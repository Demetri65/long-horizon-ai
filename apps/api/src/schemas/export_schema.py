from pydantic import TypeAdapter
from .goal import Goal
import json, pathlib

def main():
    schema = TypeAdapter(Goal).json_schema()
    schema["$id"] = "https://schemas.local/goal.schema.json"
    # write to packages/schemas_ts so web can generate types
    out = pathlib.Path(__file__).parents[4] / "packages" / "schemas_ts" / "goal.schema.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(schema, indent=2))
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()