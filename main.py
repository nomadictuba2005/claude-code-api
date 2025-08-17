#!/usr/bin/env python3
"""
Claude Code API - OpenAI Compatible API Wrapper
Wraps Claude Code CLI to provide OpenAI-compatible API endpoints
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any
import subprocess
import json
import time
import uuid
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Claude Code API",
    description="OpenAI-compatible API wrapper for Claude Code CLI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# OpenAI-compatible models
class ChatMessage(BaseModel):
    role: str = Field(..., description="The role of the message author")
    content: str = Field(..., description="The contents of the message")
    name: Optional[str] = Field(None, description="The name of the author")

class ChatCompletionRequest(BaseModel):
    model: str = Field(default="claude-sonnet-4", description="ID of the model to use")
    messages: List[ChatMessage] = Field(..., description="A list of messages comprising the conversation")
    max_tokens: Optional[int] = Field(None, description="Maximum number of tokens to generate")
    temperature: Optional[float] = Field(1.0, description="Sampling temperature")
    top_p: Optional[float] = Field(1.0, description="Nucleus sampling")
    n: Optional[int] = Field(1, description="Number of chat completion choices to generate")
    stream: Optional[bool] = Field(False, description="Whether to stream back partial progress")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Up to 4 sequences where the API will stop generating")
    presence_penalty: Optional[float] = Field(0, description="Presence penalty")
    frequency_penalty: Optional[float] = Field(0, description="Frequency penalty")
    logit_bias: Optional[Dict[str, float]] = Field(None, description="Logit bias")
    user: Optional[str] = Field(None, description="A unique identifier representing your end-user")

class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str

class ChatCompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage

class ClaudeCodeInterface:
    """Interface to Claude Code CLI"""
    
    def __init__(self):
        self.timeout = 300  # 5 minutes timeout
    
    def run_claude_command(self, message: str, model: str = "claude-sonnet-4-20250514") -> tuple[bool, str]:
        """Run Claude Code CLI command and return response"""
        try:
            logger.info(f"Executing Claude Code CLI with model {model} and message: {message[:100]}...")
            
            # Map OpenAI-style model names to Claude Code model names
            model_mapping = {
                "claude-sonnet-4": "claude-sonnet-4-20250514",
                "claude-opus-4": "claude-opus-4-20250514", 
                "claude-opus-4.1": "claude-opus-4-1-20250805",
                "claude-sonnet-3.7": "claude-3-7-sonnet-20250219",
                "claude-haiku-3.5": "claude-3-5-haiku-20241022",
                # Direct model names (already in correct format)
                "claude-sonnet-4-20250514": "claude-sonnet-4-20250514",
                "claude-opus-4-20250514": "claude-opus-4-20250514",
                "claude-opus-4-1-20250805": "claude-opus-4-1-20250805",
                "claude-3-7-sonnet-20250219": "claude-3-7-sonnet-20250219",
                "claude-3-5-haiku-20241022": "claude-3-5-haiku-20241022"
            }
            
            # Get the correct model name
            claude_model = model_mapping.get(model, "claude-sonnet-4-20250514")
            
            # Setup environment for Claude Code
            env = os.environ.copy()
            env['NODE_ENV'] = 'production'
            env['NODE_OPTIONS'] = '--max-old-space-size=512'
            env['CLAUDE_DISABLE_TELEMETRY'] = '1'
            env['CLAUDE_DISABLE_ANALYTICS'] = '1'
            
            # Use direct message with model specification
            command = f'npx claude --model {claude_model} --dangerously-skip-permissions "{message}"'
            
            logger.info(f"Running command: {command}")
            
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=os.path.expanduser('~'),
                universal_newlines=True,
                bufsize=1
            )
            
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
                
                return_code = process.returncode
                logger.info(f"Claude Code completed with return code: {return_code}")
                
                if return_code == 0:
                    # Parse Claude's response from stdout
                    response = self.extract_claude_response(stdout)
                    logger.info(f"Extracted response: {response[:200]}...")
                    return True, response
                else:
                    error_msg = stderr.strip() if stderr else f"Exit code {return_code}"
                    logger.error(f"Claude Code failed: {error_msg}")
                    return False, error_msg
                    
            except subprocess.TimeoutExpired:
                logger.error("Claude Code command timed out")
                process.kill()
                return False, "Command timed out"
                
        except Exception as e:
            logger.error(f"Error running Claude Code: {e}")
            return False, str(e)
    
    def extract_claude_response(self, output: str) -> str:
        """Extract Claude's actual response from CLI output"""
        lines = output.strip().split('\n')
        
        # Filter out CLI noise and extract the actual response
        response_lines = []
        skip_patterns = [
            "Loading project",
            "Analyzing codebase", 
            "Working directory:",
            "Press Ctrl+C",
            "Conversation saved",
            "Session",
            "───",
            "│"
        ]
        
        for line in lines:
            # Skip empty lines and CLI noise
            if not line.strip():
                continue
            
            # Skip lines that match noise patterns
            if any(pattern in line for pattern in skip_patterns):
                continue
                
            # This is likely Claude's response
            response_lines.append(line.strip())
        
        # Join the response lines
        response = '\n'.join(response_lines)
        
        # If we didn't get anything meaningful, return the raw output
        if not response or len(response) < 10:
            response = output.strip()
        
        return response

# Initialize Claude Code interface
claude_interface = ClaudeCodeInterface()

def verify_auth(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Simple auth verification - in production, implement proper API key validation"""
    if not credentials:
        return True  # For now, allow unauthenticated access
    # TODO: Implement proper API key validation
    return True

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Claude Code API - OpenAI Compatible",
        "version": "1.0.0",
        "endpoints": {
            "chat_completions": "/v1/chat/completions",
            "models": "/v1/models"
        }
    }

@app.get("/v1/models")
async def list_models(auth: bool = Depends(verify_auth)):
    """List available models (OpenAI compatible)"""
    return {
        "object": "list",
        "data": [
            {
                "id": "claude-sonnet-4",
                "object": "model", 
                "created": 1678900000,
                "owned_by": "anthropic-claude-code",
                "permission": [],
                "root": "claude-sonnet-4",
                "parent": None
            },
            {
                "id": "claude-opus-4", 
                "object": "model",
                "created": 1678900000,
                "owned_by": "anthropic-claude-code",
                "permission": [],
                "root": "claude-opus-4", 
                "parent": None
            },
            {
                "id": "claude-opus-4.1", 
                "object": "model",
                "created": 1678900000,
                "owned_by": "anthropic-claude-code",
                "permission": [],
                "root": "claude-opus-4.1", 
                "parent": None
            },
            {
                "id": "claude-sonnet-3.7", 
                "object": "model",
                "created": 1678900000,
                "owned_by": "anthropic-claude-code",
                "permission": [],
                "root": "claude-sonnet-3.7", 
                "parent": None
            },
            {
                "id": "claude-haiku-3.5", 
                "object": "model",
                "created": 1678900000,
                "owned_by": "anthropic-claude-code",
                "permission": [],
                "root": "claude-haiku-3.5", 
                "parent": None
            }
        ]
    }

@app.post("/v1/chat/completions")
async def create_chat_completion(
    request: ChatCompletionRequest,
    auth: bool = Depends(verify_auth)
) -> ChatCompletionResponse:
    """Create a chat completion (OpenAI compatible)"""
    
    try:
        logger.info(f"Received chat completion request with {len(request.messages)} messages")
        
        # Convert messages to a single prompt
        # For simplicity, we'll just use the last user message
        # In a more sophisticated implementation, you'd format the conversation properly
        user_message = ""
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_message = msg.content
                break
        
        if not user_message:
            raise HTTPException(
                status_code=400,
                detail="No user message found in the conversation"
            )
        
        # Call Claude Code CLI with specified model
        success, response = claude_interface.run_claude_command(user_message, request.model)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Claude Code CLI error: {response}"
            )
        
        # Create OpenAI-compatible response
        completion_id = f"chatcmpl-{uuid.uuid4().hex}"
        created_timestamp = int(time.time())
        
        # Estimate token usage (rough approximation)
        prompt_tokens = len(user_message.split()) * 1.3  # Rough token estimate
        completion_tokens = len(response.split()) * 1.3
        total_tokens = int(prompt_tokens + completion_tokens)
        
        return ChatCompletionResponse(
            id=completion_id,
            created=created_timestamp,
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(
                        role="assistant",
                        content=response
                    ),
                    finish_reason="stop"
                )
            ],
            usage=ChatCompletionUsage(
                prompt_tokens=int(prompt_tokens),
                completion_tokens=int(completion_tokens),
                total_tokens=total_tokens
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Quick test of Claude Code CLI
        success, _ = claude_interface.run_claude_command("Hi")
        if success:
            return {"status": "healthy", "claude_code": "available"}
        else:
            return {"status": "degraded", "claude_code": "unavailable"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)