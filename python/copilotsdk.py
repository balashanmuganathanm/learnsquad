import asyncio
import sys
from copilot import CopilotClient, PermissionHandler
from copilot.generated.session_events import SessionEventType

async def main():
    # Initialize and start the underlying Copilot CLI client
    client = CopilotClient()
    await client.start()

    # Create a session with streaming enabled
    session = await client.create_session(
        model="gpt-5.4"
    )

    # Create an event to track when the LLM finishes responding
    done = asyncio.Event()

    # Define the event listener
    def handle_event(event):
        # 1. Capture text chunks as they stream in
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            sys.stdout.write(event.data.delta_content)
            sys.stdout.flush()
        
        # 2. Complete when the model transitions back to idle
        elif event.type == SessionEventType.SESSION_IDLE:
            print("\n--- Response Complete ---")
            done.set()

    # Subscribe your handler to the session lifecycle
    session.on(handle_event)

    # Note: Modern SDK versions take a plain prompt string or dict depending on your build
    await session.send("Write a quick python function read a file.")

    # Halt code execution until the SESSION_IDLE event triggers done.set()
    await done.wait()

if __name__ == "__main__":
    asyncio.run(main())
