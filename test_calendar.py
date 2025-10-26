"""
Test script for Google Calendar integration
"""
import sys
import os

# Add the parent directory to the path so we can import from core
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.tools import get_calendar_events

def test_calendar():
    """Test the Google Calendar integration"""
    print("=" * 60)
    print("Testing Google Calendar Integration")
    print("=" * 60)
    print()
    
    # Check if credentials exist
    creds_path = os.path.join(os.path.dirname(__file__), "settings", "credentials.json")
    if not os.path.exists(creds_path):
        print("❌ credentials.json not found!")
        print(f"   Expected location: {creds_path}")
        print()
        print("Please follow the setup guide in GOOGLE_CALENDAR_SETUP.md")
        return
    else:
        print("✅ credentials.json found")
    
    print()
    print("Fetching your upcoming calendar events...")
    print("(This may open a browser window for authentication on first run)")
    print()
    
    try:
        # Get the next 5 events
        result = get_calendar_events(max_results=5)
        print(result)
        print()
        print("=" * 60)
        print("✅ Calendar integration test successful!")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Error: {e}")
        print("=" * 60)
        print()
        print("Please check:")
        print("1. Google Calendar API is enabled in Google Cloud Console")
        print("2. OAuth credentials are properly configured")
        print("3. Your email is added as a test user")
        print()
        print("See GOOGLE_CALENDAR_SETUP.md for detailed instructions")

if __name__ == "__main__":
    test_calendar()
