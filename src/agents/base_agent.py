# src/agents/base_agent.py
from google.adk import Agent
from google.generativeai import GenerativeModel
from typing import List, Callable, Optional
from src.config import settings
import logging
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BaseAgentConfig:
    """Base configuration for all Google ADK agents"""
    
    def __init__(self):
        self.api_key = settings.google_api_key
        self.default_model = "gemini-1.5-pro"
        self.temperature = 0.7
        self.max_output_tokens = 8192
        
        # Set API key for Google
        if self.api_key:
            os.environ["GOOGLE_API_KEY"] = self.api_key
    
    def get_model(self, model_name: Optional[str] = None) -> GenerativeModel:
        """Get configured Gemini model"""
        
        model = model_name or self.default_model
        
        logger.info(f"Initializing model: {model}")
        
        return GenerativeModel(
            model_name=model,
            generation_config={
                "temperature": self.temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": self.max_output_tokens,
            }
        )
    
    def create_agent(
        self,
        name: str,
        instructions: str,
        tools: List[Callable] = None,
        model_override: str = None
    ) -> Agent:
        """Create a configured ADK agent"""
        
        model = self.get_model(model_override)
        
        agent = Agent(
            name=name,
            model=model,
            tools=tools or [],
            instructions=instructions
        )
        
        logger.info(f"✅ Agent '{name}' created successfully")
        
        return agent

# Global config instance
base_config = BaseAgentConfig()
