import json

try:
    with open("tmp_openapi.json", "r") as f:
        schema = json.load(f)

    print("Looking for run endpoints...")
    for path, methods in schema.get("paths", {}).items():
        if "/runs" in path or path.endswith("/run"):
            print(f"Path: {path}")
            if "post" in methods:
                request_body = methods["post"].get("requestBody", {})
                content = request_body.get("content", {})
                schema_ref = content.get("application/json", {}).get("schema", {})
                print(f"Schema Ref: {schema_ref}")
                
                # if there is a ref, try to look it up
                if "$ref" in schema_ref:
                    ref_name = schema_ref["$ref"].split("/")[-1]
                    print(f"Ref Name: {ref_name}")
                    defined_schema = schema.get("components", {}).get("schemas", {}).get(ref_name, {})
                    print(f"Schema Definition: {json.dumps(defined_schema, indent=2)}")

except Exception as e:
    print(f"Error: {e}")
