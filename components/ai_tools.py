# components/ai_tools.py
import json

from tools.edsm_tools import EDSMAPI
from tools.knowledge_tools import KnowledgeGraphManager
from tools.journal_tools import JournalTools
import inspect
from pydantic import TypeAdapter

# Registry of tool classes (add more as needed)
TOOL_CLASSES = [EDSMAPI]

# Registry of tool methods: {method_name: (class, method_name)}
TOOL_METHODS = {}

# Populate TOOL_METHODS with public methods from registered classes
for cls in TOOL_CLASSES:
    for attr_name in dir(cls):
        if not attr_name.startswith("_"):
            attr = getattr(cls, attr_name)
            if callable(attr):
                TOOL_METHODS[attr_name] = (cls, attr_name)


def python_type_to_json_schema(py_type):
    try:
        return TypeAdapter(py_type).json_schema()
    except Exception:
        return {"type": "string"}


def _get_available_tools():
    """
    Returns a JSON string of OpenAI-compatible tool definitions for all public methods in registered tool classes.
    """
    tools = []

    for method_name, (cls, attr_name) in TOOL_METHODS.items():
        method = getattr(cls, attr_name)
        doc = method.__doc__ or ""
        sig = inspect.signature(method)

        params_schema = {"type": "object", "properties": {}, "required": []}
        # skip 'self'
        for param in list(sig.parameters.values())[1:]:
            param_type = param.annotation
            if param_type is inspect.Parameter.empty:
                schema = {"type": "string"}
            else:
                schema = python_type_to_json_schema(param_type)
            params_schema["properties"][param.name] = schema
            params_schema["required"].append(param.name)

        tools.append(
            {
                "type": "function",
                "function": {
                    "name": method_name,
                    "description": doc.strip(),
                    "parameters": params_schema,
                },
            }
        )
    return json.dumps(tools, indent=2)


def call_tool_method(method_name, **args):
    """
    Call a registered tool method by name with the given arguments.
    """
    cls, attr_name = TOOL_METHODS[method_name]
    instance = cls()
    method = getattr(instance, attr_name)
    return method(**args)
