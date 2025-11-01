"""
Smart Light Control Tool for AURA
Controls WiZ smart lights using pywizlight library
"""

import asyncio
from typing import Optional, Dict, Any, List, Tuple
from pywizlight import wizlight, PilotBuilder, discovery, SCENES
import sys


# Helper function to run async code safely on Windows
def _run_async(coro):
    """Run async code with proper event loop handling for Windows"""
    try:
        # Try to get existing loop
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        # No loop exists, create new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # On Windows, use ProactorEventLoop for better compatibility
    if sys.platform == 'win32' and not isinstance(loop, asyncio.ProactorEventLoop):
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(coro)
    except Exception as e:
        # If we get RuntimeError about closed loop, create new loop
        if "Event loop is closed" in str(e) or "NoneType" in str(e):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
        raise


class LightController:
    """Controller for WiZ smart lights"""
    
    def __init__(self):
        self.lights: Dict[str, wizlight] = {}
        self.default_ip = "192.168.0.107"  # Your light's IP
        
    def add_light(self, name: str, ip: str):
        """Add a light to the controller"""
        self.lights[name] = wizlight(ip)
        
    def get_light(self, name: Optional[str] = None) -> wizlight:
        """Get light by name or default"""
        if name and name in self.lights:
            return self.lights[name]
        # Return default light
        if not self.lights:
            self.add_light("default", self.default_ip)
        return self.lights.get("default") or list(self.lights.values())[0]


# Global controller instance
light_controller = LightController()


async def discover_lights_async(broadcast: str = "192.168.0.255") -> List[Dict[str, str]]:
    """Discover all WiZ lights in the network"""
    try:
        bulbs = await discovery.discover_lights(broadcast_space=broadcast)
        discovered = []
        for bulb in bulbs:
            discovered.append({
                "ip": bulb.ip,
                "mac": await bulb.getMac()
            })
        return discovered
    except Exception as e:
        print(f"Error discovering lights: {e}")
        return []


async def turn_on_light_async(
    light_name: Optional[str] = None,
    brightness: Optional[int] = None,
    rgb: Optional[Tuple[int, int, int]] = None,
    color_temp: Optional[int] = None,
    scene: Optional[int] = None,
    warm_white: Optional[int] = None,
    cold_white: Optional[int] = None
) -> Dict[str, Any]:
    """Turn on a light with optional parameters"""
    try:
        light = light_controller.get_light(light_name)
        
        # Build pilot with parameters
        if scene is not None:
            # Use scene
            await light.turn_on(PilotBuilder(scene=scene))
        elif rgb is not None:
            # RGB color
            pilot = PilotBuilder(rgb=rgb)
            if brightness is not None:
                pilot.set_brightness(brightness)
            await light.turn_on(pilot)
        elif color_temp is not None:
            # Color temperature
            pilot = PilotBuilder(colortemp=color_temp)
            if brightness is not None:
                pilot.set_brightness(brightness)
            await light.turn_on(pilot)
        elif warm_white is not None:
            # Warm white
            pilot = PilotBuilder(warm_white=warm_white)
            if brightness is not None:
                pilot.set_brightness(brightness)
            await light.turn_on(pilot)
        elif cold_white is not None:
            # Cold white
            pilot = PilotBuilder(cold_white=cold_white)
            if brightness is not None:
                pilot.set_brightness(brightness)
            await light.turn_on(pilot)
        elif brightness is not None:
            # Just brightness
            await light.turn_on(PilotBuilder(brightness=brightness))
        else:
            # Default - rhythm mode
            await light.turn_on(PilotBuilder())
            
        return {
            "success": True,
            "message": "Light turned on successfully",
            "light": light_name or "default"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error turning on light: {str(e)}",
            "light": light_name or "default"
        }


async def turn_off_light_async(light_name: Optional[str] = None) -> Dict[str, Any]:
    """Turn off a light"""
    try:
        light = light_controller.get_light(light_name)
        await light.turn_off()
        
        return {
            "success": True,
            "message": "Light turned off successfully",
            "light": light_name or "default"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error turning off light: {str(e)}",
            "light": light_name or "default"
        }


async def get_light_state_async(light_name: Optional[str] = None) -> Dict[str, Any]:
    """Get current state of a light"""
    try:
        light = light_controller.get_light(light_name)
        state = await light.updateState()
        
        result = {
            "success": True,
            "light": light_name or "default",
            "state": "on" if state.get_state() else "off",
            "brightness": state.get_brightness(),
        }
        
        # Add color info if available
        try:
            rgb = state.get_rgb()
            if rgb:
                result["rgb"] = rgb
        except:
            pass
            
        try:
            temp = state.get_colortemp()
            if temp:
                result["color_temp"] = temp
        except:
            pass
            
        try:
            scene = state.get_scene()
            if scene:
                result["scene"] = scene
        except:
            pass
        
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting light state: {str(e)}",
            "light": light_name or "default"
        }


async def set_brightness_async(brightness: int, light_name: Optional[str] = None) -> Dict[str, Any]:
    """Set brightness of a light (0-255)"""
    try:
        # Validate brightness
        brightness = max(0, min(255, brightness))
        
        light = light_controller.get_light(light_name)
        await light.turn_on(PilotBuilder(brightness=brightness))
        
        return {
            "success": True,
            "message": f"Brightness set to {brightness}",
            "brightness": brightness,
            "light": light_name or "default"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error setting brightness: {str(e)}",
            "light": light_name or "default"
        }


async def set_color_async(r: int, g: int, b: int, light_name: Optional[str] = None) -> Dict[str, Any]:
    """Set RGB color of a light (0-255 for each)"""
    try:
        # Validate RGB values
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        light = light_controller.get_light(light_name)
        await light.turn_on(PilotBuilder(rgb=(r, g, b)))
        
        return {
            "success": True,
            "message": f"Color set to RGB({r}, {g}, {b})",
            "rgb": (r, g, b),
            "light": light_name or "default"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error setting color: {str(e)}",
            "light": light_name or "default"
        }


async def set_scene_async(scene_id: int, light_name: Optional[str] = None) -> Dict[str, Any]:
    """Set a predefined scene (1-35)"""
    try:
        # Validate scene ID
        if scene_id < 1 or scene_id > 35:
            return {
                "success": False,
                "message": f"Invalid scene ID: {scene_id}. Must be between 1 and 35.",
                "light": light_name or "default"
            }
        
        light = light_controller.get_light(light_name)
        await light.turn_on(PilotBuilder(scene=scene_id))
        
        # Get scene name if available
        scene_name = SCENES.get(scene_id, f"Scene {scene_id}")
        
        return {
            "success": True,
            "message": f"Scene set to: {scene_name}",
            "scene_id": scene_id,
            "scene_name": scene_name,
            "light": light_name or "default"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error setting scene: {str(e)}",
            "light": light_name or "default"
        }


# Synchronous wrappers for AI tools
def turn_on_light(
    light_name: Optional[str] = None,
    brightness: Optional[int] = None,
    rgb: Optional[str] = None,
    color_temp: Optional[int] = None,
    scene: Optional[int] = None
) -> Dict[str, Any]:
    """
    Turn on a smart light with optional parameters.
    
    Args:
        light_name: Name of the light (optional, uses default if not provided)
        brightness: Brightness level 0-255 (optional)
        rgb: RGB color as "r,g,b" string (e.g., "255,0,0" for red) (optional)
        color_temp: Color temperature in Kelvin 2200-6500 (optional)
        scene: Scene ID 1-35 (optional)
    
    Returns:
        Dictionary with success status and message
    """
    # Parse RGB if provided
    rgb_tuple = None
    if rgb:
        try:
            parts = rgb.split(',')
            rgb_tuple = (int(parts[0]), int(parts[1]), int(parts[2]))
        except:
            return {"success": False, "message": "Invalid RGB format. Use 'r,g,b' (e.g., '255,0,0')"}
    
    return _run_async(turn_on_light_async(light_name, brightness, rgb_tuple, color_temp, scene))


def turn_off_light(light_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Turn off a smart light.
    
    Args:
        light_name: Name of the light (optional, uses default if not provided)
    
    Returns:
        Dictionary with success status and message
    """
    return _run_async(turn_off_light_async(light_name))


def get_light_state(light_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the current state of a smart light.
    
    Args:
        light_name: Name of the light (optional, uses default if not provided)
    
    Returns:
        Dictionary with light state information (on/off, brightness, color, etc.)
    """
    return _run_async(get_light_state_async(light_name))


def set_brightness(brightness: int, light_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Set the brightness of a smart light.
    
    Args:
        brightness: Brightness level 0-255 (0=off, 255=max brightness)
        light_name: Name of the light (optional, uses default if not provided)
    
    Returns:
        Dictionary with success status and message
    """
    return _run_async(set_brightness_async(brightness, light_name))


def set_color(r: int, g: int, b: int, light_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Set the RGB color of a smart light.
    
    Args:
        r: Red value 0-255
        g: Green value 0-255
        b: Blue value 0-255
        light_name: Name of the light (optional, uses default if not provided)
    
    Returns:
        Dictionary with success status and message
    """
    return _run_async(set_color_async(r, g, b, light_name))


def set_scene(scene_id: int, light_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Set a predefined scene for a smart light.
    
    Available scenes:
    1=Ocean, 2=Romance, 3=Sunset, 4=Party, 5=Fireplace, 6=Cozy, 7=Forest,
    8=Pastel Colors, 9=Wake up, 10=Bedtime, 11=Warm White, 12=Daylight,
    13=Cool white, 14=Night light, 15=Focus, 16=Relax, 17=True colors,
    18=TV time, 19=Plantgrowth, 20=Spring, 21=Summer, 22=Fall, 23=Deepdive,
    24=Jungle, 25=Mojito, 26=Club, 27=Christmas, 28=Halloween, 29=Candlelight,
    30=Golden white, 31=Pulse, 32=Steampunk, 33=Rhythm, 34=Diwali, 35=Snowy sky
    
    Args:
        scene_id: Scene ID number (1-35)
        light_name: Name of the light (optional, uses default if not provided)
    
    Returns:
        Dictionary with success status and message
    """
    return _run_async(set_scene_async(scene_id, light_name))


def discover_lights(broadcast: str = "192.168.0.255") -> List[Dict[str, str]]:
    """
    Discover all WiZ smart lights in the network.
    
    Args:
        broadcast: Broadcast address for discovery (default: 192.168.0.255)
    
    Returns:
        List of discovered lights with IP and MAC addresses
    """
    return _run_async(discover_lights_async(broadcast))


# Tool declarations for Gemini AI
light_declarations = [
    {
        "name": "turn_on_light",
        "description": "Turn on a smart light. Can set brightness, color, color temperature, or scene. Use this when user wants to turn on lights, set brightness, change color, or activate a scene.",
        "parameters": {
            "type": "object",
            "properties": {
                "light_name": {
                    "type": "string",
                    "description": "Name of the light to control (optional, uses default if not provided)"
                },
                "brightness": {
                    "type": "integer",
                    "description": "Brightness level 0-255. Use 255 for maximum brightness, 128 for 50%, etc."
                },
                "rgb": {
                    "type": "string",
                    "description": "RGB color as comma-separated values 'r,g,b' (e.g., '255,0,0' for red, '0,255,0' for green, '0,0,255' for blue)"
                },
                "color_temp": {
                    "type": "integer",
                    "description": "Color temperature in Kelvin (2200=warm, 4000=neutral, 6500=cool)"
                },
                "scene": {
                    "type": "integer",
                    "description": "Scene ID 1-35 (4=Party, 10=Bedtime, 15=Focus, 16=Relax, etc.)"
                }
            },
            "required": []
        }
    },
    {
        "name": "turn_off_light",
        "description": "Turn off a smart light. Use this when user wants to turn off lights.",
        "parameters": {
            "type": "object",
            "properties": {
                "light_name": {
                    "type": "string",
                    "description": "Name of the light to control (optional)"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_light_state",
        "description": "Get the current state of a smart light (on/off, brightness, color, scene). Use this when user asks about light status or current settings.",
        "parameters": {
            "type": "object",
            "properties": {
                "light_name": {
                    "type": "string",
                    "description": "Name of the light to check (optional)"
                }
            },
            "required": []
        }
    },
    {
        "name": "set_brightness",
        "description": "Set the brightness of a smart light. Use this for quick brightness adjustments.",
        "parameters": {
            "type": "object",
            "properties": {
                "brightness": {
                    "type": "integer",
                    "description": "Brightness level 0-255 (0=off, 255=maximum)"
                },
                "light_name": {
                    "type": "string",
                    "description": "Name of the light (optional)"
                }
            },
            "required": ["brightness"]
        }
    },
    {
        "name": "set_color",
        "description": "Set the RGB color of a smart light. Use this for setting specific colors.",
        "parameters": {
            "type": "object",
            "properties": {
                "r": {
                    "type": "integer",
                    "description": "Red value 0-255"
                },
                "g": {
                    "type": "integer",
                    "description": "Green value 0-255"
                },
                "b": {
                    "type": "integer",
                    "description": "Blue value 0-255"
                },
                "light_name": {
                    "type": "string",
                    "description": "Name of the light (optional)"
                }
            },
            "required": ["r", "g", "b"]
        }
    },
    {
        "name": "set_scene",
        "description": "Set a predefined scene for a smart light. Available scenes: 1=Ocean, 2=Romance, 3=Sunset, 4=Party, 5=Fireplace, 6=Cozy, 10=Bedtime, 15=Focus, 16=Relax, 27=Christmas, etc. Use this when user mentions a scene or mood.",
        "parameters": {
            "type": "object",
            "properties": {
                "scene_id": {
                    "type": "integer",
                    "description": "Scene ID number (1-35)"
                },
                "light_name": {
                    "type": "string",
                    "description": "Name of the light (optional)"
                }
            },
            "required": ["scene_id"]
        }
    },
    {
        "name": "discover_lights",
        "description": "Discover all WiZ smart lights in the network. Use this when user asks to find or discover lights.",
        "parameters": {
            "type": "object",
            "properties": {
                "broadcast": {
                    "type": "string",
                    "description": "Broadcast address for network discovery (default: 192.168.0.255)"
                }
            },
            "required": []
        }
    }
]


# Export all functions
__all__ = [
    'turn_on_light',
    'turn_off_light',
    'get_light_state',
    'set_brightness',
    'set_color',
    'set_scene',
    'discover_lights',
    'light_declarations',
    'light_controller'
]
