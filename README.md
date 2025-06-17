# Hugging Face Integrations

A collection of integration layers for various AI/ML services to work seamlessly with Hugging Face transformers and other ML libraries.

## Installation

### Development Installation

To install the package in development mode (so you can import `integrations` from anywhere):

```bash
pip install -e .
```

### Regular Installation

```bash
pip install -r requirements.txt
```

## Available Integrations

### OpenAI Integration

Provides a convenient wrapper around the OpenAI API with automatic authentication via environment variables.

```python
from integrations.openai import create_openai_client

# Create client (loads API key from .env)
client = create_openai_client()

# Use OpenAI
response = client.simple_chat("Hello! How are you?")
print(response)
```

See `integrations/openai/README.md` for detailed documentation.

## Setup

1. Create a `.env` file in your project root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

2. Install dependencies:
```bash
pip install -e .
```

3. Start using the integrations:
```python
from integrations.openai import OpenAIClient
```

## Project Structure

```
hugging/
├── integrations/           # Integration modules
│   ├── __init__.py
│   └── openai/            # OpenAI integration
│       ├── __init__.py
│       ├── client.py      # Main client
│       ├── example.py     # Usage examples
│       └── README.md      # Detailed docs
├── transformers/          # Transformers utilities
├── requirements.txt       # Dependencies
├── setup.py              # Package setup
└── README.md             # This file
```

## Contributing

1. Install in development mode: `pip install -e .`
2. Install development dependencies: `pip install -e .[dev]`
3. Run tests: `pytest`
4. Format code: `black .`
5. Check linting: `flake8`

## License

MIT License