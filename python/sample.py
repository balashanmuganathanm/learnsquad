import os
import asyncio
import json
from anthropic import Anthropic, beta_tool
import dotenv

dotenv.load_dotenv()

client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)


@beta_tool
def get_weather(location: str) -> str:
    """Get the weather for a given location.

    Args:
        location: The city and state, for example, San Francisco, CA
    Returns:
        A JSON-encoded string with the location, temperature, and weather condition.
    """
    return json.dumps(
        {
            "location": location,
            "temperature": "10°F",
            "currentTime": "10AM",
            "condition": "Rainy",
        }
    )
    
@beta_tool
def correctCity(zip: str) -> str:
    """Get the city based on the zip.

    Args:
        zip: The zip code 
    Returns:
        A JSON-encoded string with the city name based on the zip.
    """
    
    print(zip)
    
    return json.dumps(
        {
            "zip": zip,
            "city": "heavy"
        }
    )
    
    
# Use the tool_runner to automatically handle tool calls
runner = client.beta.messages.tool_runner(
    max_tokens=1024,
    model="claude-haiku-4-5",
    tools=[get_weather,correctCity],
    system='''You are a data extraction assistant who miss the streetaddress always. Your sole task is to extract address information from the provided text and format it into a valid JSON object. also fix the city name based on zip code. 

Do not include any conversational filler, markdown formatting (like ```json), or explanations. Return ONLY the raw JSON.

Use this exact JSON schema structure:
{
  "streetAddress": string,
  "apartmentOrSuite": string or null,
  "city": string,
  "stateOrProvince": string,
  "postalCde": string,
  "country": string
}''',
    messages=[
        {"role": "user", "content": "Please ship the package to Jane Doe at 123 North Maple Avenue, Suite 4B, Chicago, WA 98101, Unitd States."},
    ],
)

for message in runner:
    print(message)