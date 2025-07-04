from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json
import uvicorn
from context_handler import ContextHandler

app = FastAPI(title="Model Context Protocol Demo")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, you can specify a list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

class MCPMessage(BaseModel):
    role: str
    content: str
    
class MCPRequest(BaseModel):
    messages: List[MCPMessage]
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class MCPResponse(BaseModel):
    response: str
    context_updates: Optional[Dict[str, Any]] = Field(default_factory=dict)

# Initialize the context handler
context_handler = ContextHandler()

@app.post("/v1/chat/completions", response_model=MCPResponse)
async def chat_completion(request: MCPRequest):
    """
    Process a chat completion request with MCP support.
    """
    # Extract messages and context
    messages = request.messages
    context = request.context or {}
    
    # Get user's last message
    if not messages or messages[-1].role != "user":
        raise HTTPException(status_code=400, detail="Last message must be from user")
    
    user_message = messages[-1].content
    
    # Initialize context if needed
    if "context_id" not in context:
        user_id = "default_user"  # In a real app, this would come from authentication
        context = context_handler.create_context(user_id)
    
    # Process the message and get context updates
    context_updates = context_handler.process_message(user_message, context)
    
    # Generate a response based on the context
    response_text = generate_response(user_message, context, context_updates)
    
    return MCPResponse(
        response=response_text,
        context_updates=context_updates
    )

def generate_response(user_message: str, context: Dict[str, Any], context_updates: Dict[str, Any]) -> str:
    """
    Generate a response based on the message and context.
    In a real implementation, this would call an LLM.
    """
    # Get conversation turn count
    turn_count = context_updates.get("conversation_turns", 1)
    
    # Check for extracted entities
    entities = context_updates.get("entities", {})
    person_name = entities.get("person_name")
    location = entities.get("location")
    
    # Get sentiment
    sentiment = context_updates.get("metadata", {}).get("sentiment", "neutral")
    
    # Build response
    response_parts = []
    
    # Greet by name if available
    if person_name and "person_name" not in context.get("entities", {}):
        response_parts.append(f"Nice to meet you, {person_name}!")
    elif person_name and person_name in context.get("entities", {}).get("person_name", ""):
        response_parts.append(f"Hello again, {person_name}!")
    
    # Acknowledge location if mentioned
    if location and "location" not in context.get("entities", {}):
        response_parts.append(f"I see you're in {location}.")
    
    # Respond to the message
    if sentiment == "positive":
        response_parts.append("I'm glad you're feeling positive!")
    elif sentiment == "negative":
        response_parts.append("I'm sorry to hear that you're not feeling great.")
    
    # Add a default response if nothing specific was triggered
    if not response_parts:
        response_parts.append(f"This is conversation turn #{turn_count}. You said: {user_message}")
    else:
        response_parts.append(f"You said: {user_message}")
    
    return " ".join(response_parts)

@app.get("/")
async def root():
    return {"message": "Model Context Protocol Demo API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 