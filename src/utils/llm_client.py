"""
LLM Client Wrapper
Supports both Ollama (local) and OpenAI (cloud) for flexible deployment
"""
import os
from typing import Optional

class LLMClient:
    """Unified client for LLM interactions - supports Ollama and OpenAI"""
    
    def __init__(self):
        self.use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
        
        if self.use_ollama:
            try:
                import ollama
                self.client = ollama
                self.model = "llama3.1"
                self.provider = "ollama"
                print("✅ Using Ollama for LLM")
            except ImportError:
                print("⚠️  Ollama not available, falling back to OpenAI")
                self.use_ollama = False
        
        if not self.use_ollama:
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not set in environment")
                self.client = OpenAI(api_key=api_key)
                self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
                self.provider = "openai"
                print(f"✅ Using OpenAI ({self.model}) for LLM")
            except Exception as e:
                print(f"❌ Failed to initialize LLM client: {e}")
                raise
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text completion using configured LLM
        
        Args:
            prompt: User prompt/query
            system_prompt: System instructions (optional)
            
        Returns:
            Generated text response
        """
        if self.use_ollama:
            return self._generate_ollama(prompt, system_prompt)
        else:
            return self._generate_openai(prompt, system_prompt)
    
    def _generate_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using Ollama"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat(
            model=self.model,
            messages=messages
        )
        return response['message']['content']
    
    def _generate_openai(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using OpenAI"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content

# Global instance - import this in your agents
llm_client = LLMClient()
