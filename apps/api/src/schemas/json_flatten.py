def json_flatten(schema: dict) -> dict:
    defs = schema.get("$defs", {})
    if not defs:
        return schema

    def _deref(node):
        if isinstance(node, dict):
            if "$ref" in node and node["$ref"].startswith("#/$defs/"):
                name = node["$ref"].split("/")[-1]
                return _deref({**defs[name]})
            return {k: _deref(v) for k, v in node.items() if k != "$defs"}
        if isinstance(node, list):
            return [_deref(x) for x in node]
        return node

    flat = _deref(schema)
    flat.pop("$defs", None)
    return flat # type: ignore