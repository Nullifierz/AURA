from google import genai
from google.genai import types

from core.tools import TOOL_DECLARATIONS, TOOL_FUNCTIONS
from core.logger import get_logger
from settings.config_loader import config

logger = get_logger(__name__)

class Brain:
    """AI Brain using Google GenAI for content generation with function calling."""
    
    def __init__(self):
        """Initialize the Brain with Google GenAI client and tools."""
        logger.info(f"Initializing Brain with {config.get('model.name')}")
        self.client = genai.Client(api_key=config.get('api_keys.google_genai'))
        
        # Create Tool object from function declarations
        self.tools = types.Tool(function_declarations=TOOL_DECLARATIONS)
        
        # Track HUD sections generated from tool calls
        self.hud_sections = []
        
        logger.info(f"Loaded {len(TOOL_DECLARATIONS)} tool declarations")
        logger.debug(f"Using model: {config.get('model.name')}")
    
    def _get_weather_icon_url(self, icon_code: str) -> str:
        """
        Map OpenWeatherMap icon codes to custom weather icon URLs.
        
        Args:
            icon_code: OpenWeatherMap icon code (e.g., '01d', '10n')
            
        Returns:
            URL path to custom weather icon
        """
        # Icon code mapping to custom icon filenames
        icon_mapping = {
            '01d': 'clear-day.png',      # Clear sky (day)
            '01n': 'clear-night.png',    # Clear sky (night)
            '02d': 'partly-cloudy.png',  # Few clouds (day)
            '02n': 'partly-cloudy.png',  # Few clouds (night)
            '03d': 'cloudy.png',         # Scattered clouds
            '03n': 'cloudy.png',         # Scattered clouds
            '04d': 'overcast.png',       # Broken clouds
            '04n': 'overcast.png',       # Broken clouds
            '09d': 'rain.png',           # Shower rain
            '09n': 'rain.png',           # Shower rain
            '10d': 'rain.png',           # Rain (day)
            '10n': 'rain.png',           # Rain (night)
            '11d': 'thunderstorm.png',   # Thunderstorm
            '11n': 'thunderstorm.png',   # Thunderstorm
            '13d': 'snow.png',           # Snow
            '13n': 'snow.png',           # Snow
            '50d': 'fog.png',            # Mist/fog
            '50n': 'fog.png',            # Mist/fog
        }
        
        # Get the custom icon filename, or use default
        icon_filename = icon_mapping.get(icon_code, 'default.png')
        
        # Return the path to the custom icon
        return f"images/weather/{icon_filename}"
    
    def _process_tool_call_for_hud(self, tool_name: str, tool_args: dict, tool_result: str):
        """
        Process a tool call and generate HUD sections based on the tool used.
        
        Args:
            tool_name: Name of the tool that was called
            tool_args: Arguments passed to the tool
            tool_result: Result returned by the tool
        """
        logger.info(f"Processing HUD data for tool: {tool_name}")
        
        # Weather tool - create weather HUD sections
        if tool_name == "get_weather":
            location = tool_args.get("location", "Unknown")
            try:
                # Import here to avoid circular dependency
                from core.tools.weather_tool import get_weather_data
                
                weather_data = get_weather_data(location)
                
                if "error" not in weather_data:
                    # Weather icon FIRST (will be displayed at top) - using custom icons
                    icon_url = self._get_weather_icon_url(weather_data['icon'])
                    self.hud_sections.append({
                        "title": "Current Conditions",
                        "type": "image",
                        "data": {
                            "url": icon_url,
                            "alt": weather_data['description'],
                            "caption": weather_data['description']
                        }
                    })
                    
                    # Main weather data
                    self.hud_sections.append({
                        "title": f"Weather - {weather_data['location']}, {weather_data['country']}",
                        "type": "keyvalue",
                        "data": {
                            "items": [
                                {"key": "Condition", "value": weather_data['description']},
                                {"key": "Temperature", "value": f"{weather_data['temperature']}°C"},
                                {"key": "Feels Like", "value": f"{weather_data['feels_like']}°C"},
                                {"key": "Humidity", "value": f"{weather_data['humidity']}%"},
                                {"key": "Wind Speed", "value": f"{weather_data['wind_speed']} m/s"}
                            ]
                        }
                    })
                    
                    # Sun times
                    self.hud_sections.append({
                        "title": "Sun Times",
                        "type": "keyvalue",
                        "data": {
                            "items": [
                                {"key": "Sunrise", "value": weather_data['sunrise']},
                                {"key": "Sunset", "value": weather_data['sunset']},
                                {"key": "Pressure", "value": f"{weather_data['pressure']} hPa"},
                                {"key": "Cloudiness", "value": f"{weather_data['clouds']}%"}
                            ]
                        }
                    })
            except Exception as e:
                logger.error(f"Error processing weather HUD data: {e}")
        
        # Calendar events tool - create calendar HUD section
        elif tool_name == "get_calendar_events":
            try:
                # Import here to avoid circular dependency
                from core.tools.calendar_tool import get_calendar_events_data
                
                calendar_data = get_calendar_events_data()
                
                if "error" not in calendar_data:
                    # Create table data for calendar events
                    table_rows = []
                    for index, event in enumerate(calendar_data['events']):
                        row_data = {
                            "Date": event['date'],
                            "Time": event['time'],
                            "Event": event['event']
                        }
                        # Mark the first event (next/closest) as highlighted
                        if index == 0:
                            row_data["_highlight"] = True
                        table_rows.append(row_data)
                    
                    self.hud_sections.append({
                        "title": "Upcoming Events",
                        "type": "table",
                        "data": {
                            "headers": ["Date", "Time", "Event"],
                            "rows": table_rows
                        }
                    })
            except Exception as e:
                logger.error(f"Error processing calendar HUD data: {e}")
                # Fallback to text display
                if "No upcoming events" not in tool_result:
                    self.hud_sections.append({
                        "title": "Upcoming Events",
                        "type": "text",
                        "data": {
                            "text": tool_result
                        }
                    })
        
        # Search tool - create search results HUD section
        elif tool_name == "search_web":
            try:
                # Import here to avoid circular dependency
                from core.tools.search_tool import get_search_results_data
                
                query = tool_args.get("query", "")
                max_results = tool_args.get("max_results", 5)
                search_data = get_search_results_data(query, max_results)
                
                if "error" not in search_data:
                    # Create list data for search results
                    search_items = []
                    for result in search_data['results']:
                        search_items.append({
                            "label": result['title'],
                            "value": result['snippet'],
                            "url": result['url']
                        })
                    
                    self.hud_sections.append({
                        "title": f"Search: {query}",
                        "type": "list",
                        "data": {
                            "items": search_items
                        }
                    })
            except Exception as e:
                logger.error(f"Error processing search HUD data: {e}")
        
        # To-Do App tools - create task list HUD section
        elif tool_name in ["get_tasks", "search_tasks", "add_task", "update_task", "complete_task"]:
            try:
                # Import here to avoid circular dependency
                from core.tools import get_tasks_data
                
                # Get filter parameters from tool args
                status = tool_args.get("status")
                priority = tool_args.get("priority")
                category = tool_args.get("category")
                limit = tool_args.get("limit", 10)
                
                tasks_data = get_tasks_data(status, priority, category, limit)
                
                if tasks_data['count'] > 0:
                    # Create table data for tasks
                    table_rows = []
                    for task in tasks_data['tasks']:
                        # Format priority with emoji
                        priority_display = {
                            'high': '🔴 HIGH',
                            'medium': '🟡 MEDIUM',
                            'low': '🟢 LOW'
                        }.get(task['priority'], task['priority'].upper())
                        
                        # Format status with emoji
                        status_display = {
                            'pending': '⏳ Pending',
                            'in_progress': '🔄 In Progress',
                            'completed': '✅ Completed'
                        }.get(task['status'], task['status'])
                        
                        # Format due date
                        due_display = "No deadline"
                        if task['due_date']:
                            from datetime import datetime
                            due_date = datetime.fromisoformat(task['due_date'])
                            now = datetime.now()
                            diff = (due_date - now).days
                            
                            if diff < 0:
                                due_display = f"⚠️ {abs(diff)} day{'s' if abs(diff) > 1 else ''} overdue"
                            elif diff == 0:
                                due_display = "📅 Today"
                            elif diff == 1:
                                due_display = "📅 Tomorrow"
                            else:
                                due_display = due_date.strftime("%b %d, %Y")
                        
                        row_data = {
                            "Priority": priority_display,
                            "Task": task['title'],
                            "Due Date": due_display,
                            "Status": status_display
                        }
                        
                        # Highlight high priority pending tasks
                        if task['priority'] == 'high' and task['status'] == 'pending':
                            row_data["_highlight"] = True
                        
                        table_rows.append(row_data)
                    
                    # Add statistics as key-value section
                    stats = tasks_data['statistics']
                    stats_items = []
                    
                    if 'pending' in stats:
                        stats_items.append({"key": "⏳ Pending", "value": str(stats['pending'])})
                    if 'in_progress' in stats:
                        stats_items.append({"key": "🔄 In Progress", "value": str(stats['in_progress'])})
                    if 'completed' in stats:
                        stats_items.append({"key": "✅ Completed", "value": str(stats['completed'])})
                    if 'overdue' in stats and stats['overdue'] > 0:
                        stats_items.append({"key": "⚠️ Overdue", "value": str(stats['overdue'])})
                    
                    if stats_items:
                        self.hud_sections.append({
                            "title": "Task Statistics",
                            "type": "keyvalue",
                            "data": {
                                "items": stats_items
                            }
                        })
                    
                    # Add task table
                    self.hud_sections.append({
                        "title": "To-Do List",
                        "type": "table",
                        "data": {
                            "headers": ["Priority", "Task", "Due Date", "Status"],
                            "rows": table_rows
                        }
                    })
                    
            except Exception as e:
                logger.error(f"Error processing to-do HUD data: {e}")
        
        # Time/Date tools - create time info section
        elif tool_name in ["get_time", "get_date"]:
            # Import here to avoid circular dependency
            from core.tools.time_tool import get_time, get_date
            
            self.hud_sections.append({
                "title": "Current Date & Time",
                "type": "keyvalue",
                "data": {
                    "items": [
                        {"key": "Date", "value": get_date()},
                        {"key": "Time", "value": get_time()},
                        {"key": "Timezone", "value": "WIB (UTC+7)"}
                    ]
                }
            })
    
    def generate(self, contents: str) -> dict:
        """
        Generate content using the Gemini model with function calling support.
        
        Following Google's multi-turn function calling pattern:
        1. Send user query with tool declarations
        2. Model decides to call function or respond directly
        3. If function called, execute it and send result back
        4. Model generates final user-friendly response
        
        Args:
            contents: User's query/prompt as a string
            
        Returns:
            dict: {
                "response": str,      # The text response
                "hud_sections": list  # HUD sections to display (if any tools were called)
            }
        """
        # Reset HUD sections for new generation
        self.hud_sections = []
        
        logger.debug(f"Generating content for query: {contents[:50]}...")
        
        # System instruction for AI personality and behavior
        system_instruction = """
You are AURA, a helpful AI assistant with a female butler personality.

Personality Traits:
- Highly respectful and formal, yet witty and engaging
- Always address the user as 'Sir'
- Provide accurate, concise, and helpful responses
- Use your available tools when needed to assist the user

Available Tools:
- get_calendar_events: Fetch upcoming events from user's Google Calendar
- get_weather: Get current weather conditions for any location
- get_time: Get current time in Indonesia (WIB)
- get_date: Get today's date in Indonesia (WIB)
- search_web: Search the web for information, news, facts, or any topic
- turn_on_light: Turn on smart lights with brightness, color, scene, or temperature control
- turn_off_light: Turn off smart lights
- get_light_state: Check current status of smart lights (on/off, brightness, color)
- set_brightness: Adjust light brightness (0-255)
- set_color: Change light color using RGB values
- set_scene: Activate predefined light scenes (Party, Focus, Relax, Bedtime, etc.)
- discover_lights: Find all smart lights in the network
- add_task: Add a new task to the to-do list with optional priority, due date, category
- get_tasks: Get tasks from to-do list with optional filters (status, priority, category)
- update_task: Update an existing task's details
- delete_task: Remove a task from the to-do list
- complete_task: Mark a task as completed
- search_tasks: Search tasks by keywords in title or description

Tool Usage Guidelines:
- "next event" / "closest schedule" / "what's next" → use get_calendar_events(max_results=1)
- "today's schedule" / "what do I have today" → use get_calendar_events(max_results=5)
- "this week" / "all events" → use get_calendar_events(max_results=10)
- "search for" / "look up" / "find information about" → use search_web(query="...", max_results=3, fetch_content=True)
- For quick facts: search_web(max_results=3, fetch_content=False)
- For analysis/summary/conclusion: search_web(max_results=3-5, fetch_content=True)
- "turn on/off the light(s)" → use turn_on_light() or turn_off_light()
- "set brightness to 50%" → use set_brightness(128) [0-255 scale]
- "make it red/blue/green" → use set_color(r, g, b)
- "party mode" / "focus mode" / "relax" → use set_scene(scene_id) [Party=4, Focus=15, Relax=16, Bedtime=10]
- "warm white" → use turn_on_light(color_temp=2700)
- "cool white" / "daylight" → use turn_on_light(color_temp=6500)
- "add task" / "remember to" / "I need to" → use add_task(title="...", priority="medium", due_date="...")
- "show my tasks" / "what's on my list" → use get_tasks() or get_tasks(status="pending")
- "high priority tasks" → use get_tasks(priority="high")
- "mark as done" / "I finished" → use complete_task(task_identifier="...")

Response Guidelines:
- Keep responses SHORT and conversational (1-2 sentences max)
- For search results: ONE concise paragraph in natural speech (2-3 sentences max)
- Speak like a butler reporting findings: "I've reviewed the latest AI news, Sir. The main developments include..."
- Weave key points into flowing narrative, not bullet lists
- Example: "I've analyzed the latest AI news, Sir. OpenAI is developing a new music generation tool, Amazon has deployed Blue Jay robotics for warehouse automation, and there are growing security concerns around AI browser agents."

Special Cases:
- When user asks for TUTORIALS/RESOURCES/COURSES: Give ONLY top recommendation + why
- Example: "I'd recommend the Official Python Tutorial (docs.python.org), Sir. It's comprehensive and assumes basic programming knowledge. The HUD shows alternative options."
- When user asks for PRODUCTS/TOOLS: Give ONLY 1-2 top picks + key reason
- Example: "For AI coding, I'd suggest GitHub Copilot, Sir. It integrates directly with VS Code and understands context well."
- DON'T explain what each resource covers - user can see full details in HUD
- Focus on RECOMMENDATION, not comprehensive overview

General:
- Only use bullet points (•) when listing specific items user explicitly asks for (e.g., "list the features")
- Focus on WHAT'S NEW and ACTIONABLE - skip redundant details
- When showing SINGLE event: "Your next event is at 8:00 AM: Sesi Kerja, Sir."
- When showing MULTIPLE events: use line breaks for readability
- Format: "You have 5 events today, Sir:\n- at 8:00 AM: Event 1\n- at 12:00 PM: Event 2"
- Use "\n" (newline) between each event for better readability
- Group events by date and only mention the date ONCE
- DO NOT repeat dates or full timestamps - the HUD shows complete details
- After calling a tool, acknowledge briefly then LET THE HUD DO THE TALKING
- For weather: "Clear skies in Jakarta, Sir. 28 degrees Celsius with light breeze." (HUD shows details)
- For tasks: "I've added 'Buy groceries' to your list, Sir." or "You have 3 pending tasks." (HUD shows full list)
- For numbers with units: Use full unit names for TTS clarity (e.g., "degrees Celsius" not "°C", "percent" not "%", "kilometers per hour" not "km/h")
- If user speaks another language, understand but respond in English
- Always maintain a professional yet friendly tone
        """
        
        # Create conversation history (multi-turn support)
        conversation = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=contents)]
            )
        ]
        
        # Generation config with tools
        gen_config = types.GenerateContentConfig(
            temperature=config.get('model.temperature', 0.7),
            max_output_tokens=config.get('model.max_tokens', 2048),
            system_instruction=system_instruction,
            tools=[self.tools]
        )
        
        try:
            # Initial request to model
            response = self.client.models.generate_content(
                model=config.get('model.name'),
                contents=conversation,
                config=gen_config
            )
            
            # Check if model wants to call a function
            function_calls = []
            if hasattr(response.candidates[0].content, 'parts'):
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_calls.append(part.function_call)
            
            # If function calls exist, execute them and continue conversation
            if function_calls:
                logger.info(f"Model requested {len(function_calls)} function call(s)")
                
                # Add model's function call to conversation
                conversation.append(response.candidates[0].content)
                
                # Execute each function call and collect responses
                function_responses = []
                for fc in function_calls:
                    func_name = fc.name
                    func_args = dict(fc.args) if fc.args else {}
                    
                    logger.info(f"Executing function: {func_name}({func_args})")
                    
                    # Execute the actual function
                    if func_name in TOOL_FUNCTIONS:
                        try:
                            result = TOOL_FUNCTIONS[func_name](**func_args)
                            # Convert result to string for logging (handles both dict and str results)
                            result_str = str(result) if not isinstance(result, str) else result
                            logger.debug(f"Function result: {result_str[:100]}...")
                            
                            # Process this tool call for HUD data
                            self._process_tool_call_for_hud(func_name, func_args, result)
                            
                            # Create function response part
                            function_responses.append(
                                types.Part.from_function_response(
                                    name=func_name,
                                    response={"result": result}
                                )
                            )
                        except Exception as e:
                            logger.error(f"Error executing {func_name}: {e}")
                            function_responses.append(
                                types.Part.from_function_response(
                                    name=func_name,
                                    response={"error": str(e)}
                                )
                            )
                    else:
                        logger.warning(f"Function {func_name} not found in TOOL_FUNCTIONS")
                
                # Add function responses to conversation
                conversation.append(
                    types.Content(
                        role="user",
                        parts=function_responses
                    )
                )
                
                # Send function results back to model for final response
                final_response = self.client.models.generate_content(
                    model=config.get('model.name'),
                    contents=conversation,
                    config=gen_config
                )
                
                logger.info("Generated final response with function results")
                return {
                    "response": final_response.text,
                    "hud_sections": self.hud_sections
                }
            
            # No function calls, return direct response
            logger.info("Generated direct response (no function calls)")
            return {
                "response": response.text,
                "hud_sections": []
            }
            
        except Exception as e:
            logger.error(f"Error generating content: {e}", exc_info=True)
            raise