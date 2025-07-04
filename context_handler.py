from typing import Dict, Any, List, Optional
import json
import time
import uuid

class ContextHandler:
    def __init__(self):
        # In-memory storage for context
        self.contexts = {}
    
    def create_context(self, user_id: str) -> Dict[str, Any]:
        """
        Create a new context for a user.
        """
        context_id = str(uuid.uuid4())
        context = {
            "context_id": context_id,
            "user_id": user_id,
            "created_at": time.time(),
            "updated_at": time.time(),
            "conversation_turns": 0,
            "metadata": {},
            "entities": {},
            "preferences": {}
        }
        self.contexts[context_id] = context
        return context
    
    def get_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a context by ID.
        """
        return self.contexts.get(context_id)
    
    def update_context(self, context_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a context with new information.
        """
        if context_id not in self.contexts:
            return None
        
        context = self.contexts[context_id]
        
        # Update specific sections based on the updates
        for key, value in updates.items():
            if key in ["metadata", "entities", "preferences"] and isinstance(value, dict):
                if key not in context:
                    context[key] = {}
                context[key].update(value)
            else:
                context[key] = value
        
        # Update the timestamp
        context["updated_at"] = time.time()
        
        return context
    
    def extract_entities(self, message: str) -> Dict[str, Any]:
        """
        Simple entity extraction from user message.
        In a real implementation, this would use NLP techniques.
        """
        entities = {}
        
        # Simple name detection (very basic)
        if "my name is" in message.lower():
            parts = message.lower().split("my name is")
            if len(parts) > 1:
                name = parts[1].strip().split()[0].capitalize()
                entities["person_name"] = name
        
        # Simple location detection
        if "i am in" in message.lower() or "i'm in" in message.lower():
            location_phrase = "i am in" if "i am in" in message.lower() else "i'm in"
            parts = message.lower().split(location_phrase)
            if len(parts) > 1:
                location = parts[1].strip().split(".")[0].capitalize()
                entities["location"] = location
        
        return {"entities": entities}
    
    def process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user message and extract context updates.
        """
        context_updates = {}
        
        # Update conversation turns
        conversation_turns = context.get("conversation_turns", 0) + 1
        context_updates["conversation_turns"] = conversation_turns
        
        # Extract entities
        entity_updates = self.extract_entities(message)
        if entity_updates.get("entities"):
            context_updates.update(entity_updates)
        
        # Extract sentiment (simplified)
        positive_words = ["happy", "good", "great", "excellent", "love", "like"]
        negative_words = ["sad", "bad", "terrible", "hate", "dislike"]
        
        words = message.lower().split()
        sentiment = "neutral"
        
        if any(word in words for word in positive_words):
            sentiment = "positive"
        elif any(word in words for word in negative_words):
            sentiment = "negative"
        
        context_updates["metadata"] = {"sentiment": sentiment, "last_message_time": time.time()}
        
        return context_updates 