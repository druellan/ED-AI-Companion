import os
import importlib

EVENT_PARSERS = {}

# Get the directory containing the parser modules
parsers_dir = os.path.dirname(__file__)

# Iterate through all .py files in the parsers directory
for filename in os.listdir(parsers_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = filename[:-3]
        try:
            # Import the module
            module = importlib.import_module(f"parsers.{module_name}")

            # Check if the module has both parse function and CONTEXT
            if hasattr(module, "parse") and hasattr(module, "CONTEXT"):
                # Convert module_name to event name (e.g., 'receivetext' -> 'ReceiveText')
                event_name = module_name

                EVENT_PARSERS[event_name] = {
                    "function": module.parse,
                    "context": module.CONTEXT,
                }
                print(f"Loaded parser for {event_name}")

        except ImportError as e:
            print(f"Error importing {module_name}: {e}")
