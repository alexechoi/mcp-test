import requests
import json
from typing import Dict, Any, List
import time
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

class MCPClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.context = {}
        self.conversation_history = []
    
    def send_message(self, message: str) -> Dict[str, Any]:
        """
        Send a message to the MCP API and update the local context.
        """
        # Add the new message to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Prepare the request payload
        payload = {
            "messages": self.conversation_history,
            "context": self.context
        }
        
        # Send the request to the API
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload
            )
            
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                print(response.text)
                return {}
            
            # Parse the response
            result = response.json()
            
            # Update the local context with any context updates
            if "context_updates" in result:
                self.context.update(result["context_updates"])
            
            # Add the assistant's response to conversation history
            self.conversation_history.append({"role": "assistant", "content": result["response"]})
            
            return result
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to the server. Make sure the server is running.")
            return {"response": "Connection error. Server might not be running."}
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get the current context.
        """
        return self.context
    
    def display_context(self):
        """
        Display the current context in a formatted way.
        """
        if not self.context:
            print("\nContext is empty.")
            return
        
        print("\n===== CONTEXT =====")
        
        if "context_id" in self.context:
            print(f"Context ID: {self.context['context_id']}")
        
        if "user_id" in self.context:
            print(f"User ID: {self.context['user_id']}")
        
        if "conversation_turns" in self.context:
            print(f"Conversation Turns: {self.context['conversation_turns']}")
        
        if "created_at" in self.context:
            created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.context["created_at"]))
            print(f"Created At: {created_time}")
        
        if "updated_at" in self.context:
            updated_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.context["updated_at"]))
            print(f"Updated At: {updated_time}")
        
        # Display entities
        if "entities" in self.context and self.context["entities"]:
            print("\n--- Entities ---")
            for key, value in self.context["entities"].items():
                print(f"{key}: {value}")
        
        # Display metadata
        if "metadata" in self.context and self.context["metadata"]:
            print("\n--- Metadata ---")
            for key, value in self.context["metadata"].items():
                if key == "last_message_time":
                    value = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))
                print(f"{key}: {value}")
        
        # Display preferences
        if "preferences" in self.context and self.context["preferences"]:
            print("\n--- Preferences ---")
            for key, value in self.context["preferences"].items():
                print(f"{key}: {value}")
        
        print("=================")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>MCP Client</title>
        </head>
        <body>
            <h1>MCP Client</h1>
            <form action="/send" method="post">
                <input type="text" name="message" placeholder="Type your message here" required>
                <button type="submit">Send</button>
            </form>
            <button onclick="checkHealth()">Check Health</button>
            <div id="response"></div>
            <script>
                function checkHealth() {
                    fetch('http://localhost:8000/health')
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('response').innerHTML = JSON.stringify(data);
                        })
                        .catch(error => {
                            document.getElementById('response').innerHTML = 'Error: ' + error;
                        });
                }
            </script>
        </body>
    </html>
    """

@app.post("/send", response_class=HTMLResponse)
async def send_message(message: str = Form(...)):
    client = MCPClient()
    result = client.send_message(message)
    response_text = result.get("response", "No response from server.")
    return f"<html><body><h2>Response:</h2><p>{response_text}</p><a href='/'>Back</a></body></html>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 