# Tools Module Restructuring

## Overview
Restructured the tools module to follow Google's Gemini API best practices for function calling, implementing a modular architecture where each tool is self-contained with its declaration and implementation.

## New Structure

```
core/tools/
├── __init__.py              # Package exports and tool registry
├── calendar_tool.py         # Google Calendar integration
├── weather_tool.py          # OpenWeatherMap integration
└── time_tool.py            # Time and date utilities
```

## Key Changes

### 1. Function Declarations (Google's Schema)
Each tool now includes a proper function declaration following OpenAPI schema:

```python
weather_declaration = {
    "name": "get_weather",
    "description": "Gets the current weather conditions...",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city name or location...",
            },
            "temperature": {
                "type": "string",
                "enum": ["C", "F"]
            }
        },
        "required": ["location"]
    }
}
```

### 2. Modular Tool Files

**calendar_tool.py**
- `calendar_declaration`: Function schema for Gemini
- `get_calendar_events()`: Implementation
- `_get_calendar_service()`: Helper (lazy imports)

**weather_tool.py**
- `weather_declaration`: Function schema for Gemini
- `get_weather()`: For AI conversation (tool-callable)
- `get_weather_data()`: For HUD display (internal only)

**time_tool.py**
- `time_declaration`: Function schema for get_time
- `date_declaration`: Function schema for get_date
- `get_time()`: Implementation
- `get_date()`: Implementation

### 3. Central Registry (__init__.py)

```python
TOOL_DECLARATIONS = [
    calendar_declaration,
    weather_declaration,
    time_declaration,
    date_declaration
]

TOOL_FUNCTIONS = {
    "get_calendar_events": get_calendar_events,
    "get_weather": get_weather,
    ...
}
```

## Brain.py Improvements

### Multi-Turn Function Calling
Implemented Google's recommended pattern:

1. **Send query with tool declarations**
   ```python
   tools = types.Tool(function_declarations=TOOL_DECLARATIONS)
   ```

2. **Detect function calls**
   ```python
   if hasattr(part, 'function_call') and part.function_call:
       function_calls.append(part.function_call)
   ```

3. **Execute functions**
   ```python
   result = TOOL_FUNCTIONS[func_name](**func_args)
   ```

4. **Send results back**
   ```python
   function_responses.append(
       types.Part.from_function_response(
           name=func_name,
           response={"result": result}
       )
   )
   ```

5. **Get final response**
   ```python
   final_response = client.models.generate_content(...)
   ```

### Conversation History
Maintains proper conversation context:
```python
conversation = [
    types.Content(role="user", parts=[...]),  # User query
    types.Content(role="model", parts=[...]), # Function call
    types.Content(role="user", parts=[...])   # Function result
]
```

## Benefits

✅ **Follows Google's Best Practices**: Matches official documentation exactly
✅ **Modular Architecture**: Each tool is self-contained and testable
✅ **Clear Separation**: Declaration vs. implementation
✅ **Extensible**: Easy to add new tools
✅ **Type Safety**: Proper enums and required fields
✅ **Better Descriptions**: Detailed parameter descriptions for AI
✅ **Multi-Turn Support**: Handles complex function calling flows
✅ **Error Handling**: Proper try/catch for function execution

## Usage

### Adding a New Tool

1. Create `core/tools/new_tool.py`:
```python
tool_declaration = {
    "name": "do_something",
    "description": "...",
    "parameters": {...}
}

def do_something(param1: str) -> str:
    """Implementation"""
    return "result"
```

2. Update `core/tools/__init__.py`:
```python
from .new_tool import do_something, tool_declaration

TOOL_DECLARATIONS.append(tool_declaration)
TOOL_FUNCTIONS["do_something"] = do_something
```

3. That's it! Brain will automatically use it.

## Testing

Test individual tools:
```python
from core.tools.weather_tool import get_weather

result = get_weather("Jakarta", "C")
print(result)
```

Test with Brain:
```python
from core.brain import Brain

brain = Brain()
response = brain.generate("What's the weather in London?")
print(response)
```

## Migration Notes

- Old `core/tools.py` can be deleted
- All imports updated to use new module structure
- `main.py` updated to import from `core.tools.weather_tool`
- No breaking changes to existing functionality
