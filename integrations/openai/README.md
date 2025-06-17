# OpenAI Integration

A convenient Python wrapper for the OpenAI API that handles authentication via environment variables and provides both synchronous and asynchronous interfaces.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Environment Variables

Create a `.env` file in your project root:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional: If you have an organization ID
OPENAI_ORG_ID=your_organization_id_here
```

**Note**: Never commit your `.env` file to version control. Add it to your `.gitignore`.

### 3. Get Your OpenAI API Key

1. Go to [OpenAI's API Keys page](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key and add it to your `.env` file

## Usage

### Basic Usage

```python
from integrations.openai import create_openai_client

# Create client (automatically loads from .env)
client = create_openai_client()

# Simple chat
response = client.simple_chat("Hello! How are you?")
print(response)
```

### Advanced Chat Completion

```python
from integrations.openai import OpenAIClient

client = OpenAIClient()

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing briefly."}
]

response = client.chat_completion(
    messages=messages,
    model="gpt-4",  # or "gpt-3.5-turbo"
    temperature=0.7,
    max_tokens=200
)

print(response.choices[0].message.content)
```

### Text Completion

```python
client = OpenAIClient()

response = client.simple_complete(
    "The future of artificial intelligence is"
)
print(response)
```

### Embeddings

```python
client = OpenAIClient()

# Single text
embedding = client.get_embedding_vector("Hello world")
print(f"Embedding dimension: {len(embedding)}")

# Multiple texts
response = client.create_embeddings([
    "First text",
    "Second text",
    "Third text"
])
```

### Async Usage

```python
import asyncio
from integrations.openai import OpenAIClient

async def async_example():
    client = OpenAIClient()

    messages = [{"role": "user", "content": "Hello!"}]
    response = await client.async_chat_completion(messages)
    print(response.choices[0].message.content)

# Run async function
asyncio.run(async_example())
```

### List Available Models

```python
client = OpenAIClient()
models = client.list_models()
print(f"Available models: {len(models)}")
for model in models[:5]:  # Show first 5
    print(f"  - {model}")
```

## Available Methods

### OpenAIClient Class

- `chat_completion()` - Create chat completions with full control
- `async_chat_completion()` - Async version of chat completion
- `completion()` - Create text completions
- `create_embeddings()` - Generate text embeddings
- `list_models()` - List available OpenAI models
- `simple_chat()` - Easy-to-use chat interface
- `simple_complete()` - Easy-to-use completion interface
- `get_embedding_vector()` - Get embedding for single text

### Convenience Functions

- `create_openai_client()` - Factory function to create client instance

## Configuration Options

The client supports the following environment variables:

- `OPENAI_API_KEY` (required) - Your OpenAI API key
- `OPENAI_ORG_ID` (optional) - Your OpenAI organization ID

You can also pass these directly to the client:

```python
client = OpenAIClient(
    api_key="your-key-here",
    organization="your-org-id"
)
```

## Error Handling

The client includes built-in error handling and logging:

```python
import logging

# Configure logging to see client messages
logging.basicConfig(level=logging.INFO)

client = OpenAIClient()

try:
    response = client.simple_chat("Hello!")
    print(response)
except Exception as e:
    print(f"Error: {e}")
```

## Examples

Run the example file to see all features in action:

```bash
python integrations/openai/example.py
```

Make sure you have set your `OPENAI_API_KEY` in the `.env` file first!

## Supported Models

The client works with all OpenAI models including:

- **Chat Models**: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
- **Completion Models**: `gpt-3.5-turbo-instruct`
- **Embedding Models**: `text-embedding-3-small`, `text-embedding-3-large`, `text-embedding-ada-002`

Use `client.list_models()` to see all currently available models.

## Requirements

- Python 3.7+
- openai >= 1.35.0
- python-dotenv >= 1.0.0