# Claude Code API

**OpenAI-compatible REST API wrapper for Claude Code CLI**

Transform your Claude Code CLI into a standard REST API that works with any OpenAI-compatible client library or tool.

## What It Does

This project creates a FastAPI server that:
- ✅ **Accepts OpenAI API requests** at standard endpoints (`/v1/chat/completions`, `/v1/models`)
- ✅ **Translates requests to Claude Code CLI calls** with proper model selection
- ✅ **Returns OpenAI-format responses** with usage statistics
- ✅ **Works with any OpenAI client library** (Python, JavaScript, curl, etc.)
- ✅ **Supports all Claude models** (Sonnet 4, Opus 4, Haiku 3.5, etc.)

## Quick Start

### Prerequisites
- **Claude Code CLI** installed and authenticated (`claude login`)
- **Python 3.8+** with pip
- **Node.js 18+** (for Claude Code)

### Installation
```bash
git clone https://github.com/nomadictuba2005/claude-code-api.git
cd claude-code-api
pip install fastapi uvicorn pydantic
```

### Start the Server
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Test It Works
```bash
python test_api.py
```

## Usage Examples

### Python (openai library)
```python
import openai

client = openai.OpenAI(
    api_key="not-needed",  # Claude Code uses CLI auth
    base_url="http://localhost:8000/v1"
)

response = client.chat.completions.create(
    model="claude-sonnet-4",
    messages=[
        {"role": "user", "content": "Write a hello world program in Python"}
    ]
)

print(response.choices[0].message.content)
```

### JavaScript
```javascript
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: 'not-needed',
  baseURL: 'http://localhost:8000/v1',
});

const completion = await openai.chat.completions.create({
  messages: [{ role: 'user', content: 'Explain async/await in JavaScript' }],
  model: 'claude-sonnet-4',
});

console.log(completion.choices[0].message.content);
```

### curl
```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4", 
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ]
  }'
```

## Available Models

- `claude-sonnet-4` - Latest Sonnet model for daily development
- `claude-opus-4` - Most capable model for complex reasoning
- `claude-opus-4.1` - Latest Opus model with enhanced capabilities
- `claude-sonnet-3.7` - Previous generation Sonnet model
- `claude-haiku-3.5` - Fastest model for simple tasks

## API Endpoints

### POST `/v1/chat/completions`
OpenAI-compatible chat completions endpoint.

**Request:**
```json
{
  "model": "claude-sonnet-4",
  "messages": [
    {"role": "user", "content": "Your message here"}
  ],
  "max_tokens": 100,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1678900000,
  "model": "claude-sonnet-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Claude's response here"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### GET `/v1/models`
List available models.

### GET `/health`
Health check endpoint.

## Use Cases

### 🔧 **Local Development**
Use Claude Code as a drop-in replacement for OpenAI API in your local projects.

### 🚀 **Existing Applications**
Integrate Claude Code into apps that already use OpenAI API without code changes.

### 🧪 **Testing & Prototyping**
Test your OpenAI API integrations using Claude Code locally before deploying.

### 📚 **Learning & Education**
Use familiar OpenAI API patterns to interact with Claude models.

## How It Works

1. **Receives OpenAI API request** → Extracts user message and model
2. **Calls Claude Code CLI** → `npx claude --model <model> "message"`
3. **Parses CLI output** → Filters out CLI noise, extracts response
4. **Returns OpenAI format** → Standard JSON response with usage stats

## Configuration

### Environment Variables
- `CLAUDE_TIMEOUT`: Timeout for Claude Code CLI calls (default: 300 seconds)
- `API_PORT`: Port to run the server on (default: 8000)

### Production Deployment
For production use:
1. Add proper authentication (modify `verify_auth` function)
2. Implement rate limiting
3. Add request logging and monitoring
4. Use a production WSGI server (gunicorn, etc.)

## Limitations

- **Single-turn conversations** (doesn't maintain conversation history yet)
- **No streaming support** (planned for future release)
- **Basic response parsing** (filters Claude Code CLI output)
- **Uses Claude Code's rate limits** (no additional limiting)

## System Requirements

- **RAM:** 512MB+ (1GB+ recommended for multiple concurrent requests)
- **CPU:** Any modern processor
- **Storage:** 100MB for installation
- **Network:** Internet connection for Claude Code CLI

## Troubleshooting

### Claude Code Not Found
```bash
# Verify Claude Code installation
claude --version
which claude

# If missing, reinstall:
npm install -g @anthropic-ai/claude-code
```

### Authentication Errors
```bash
# Re-login to Claude Code
claude login

# Test authentication
claude "Hi"
```

### Permission Denied
```bash
# Check if Claude Code CLI works
npx claude --version

# Verify you're authenticated
npx claude "test message"
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - Use it however you want!

---

**Made by [@nomadictuba2005](https://github.com/nomadictuba2005)**

*OpenAI-compatible Claude Code API since 2025* 🚀

**⭐ Star this repo if it helps you integrate Claude Code into your workflow!**