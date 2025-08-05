# Web Search Tool with Pydantic-AI - Implementation Plan

## Overview
This plan outlines the implementation of a web search tool using pydantic-ai that can search DuckDuckGo's XML API and switch between OpenAI and Ollama integrations for AI processing.

## Architecture Components

### 1. Core Components
- **Web Search Tool**: DuckDuckGo XML API integration
- **AI Integration Layer**: Abstract interface for OpenAI/Ollama
- **Agent System**: Pydantic-ai based agent with tool calling
- **Configuration System**: Easy switching between AI providers

### 2. Project Structure
```
integrations/
├── ollama/
│   ├── __init__.py
│   ├── ollama_client.py          # Ollama client implementation
│   └── ollama_agent.py           # Ollama-specific agent
├── openai/
│   ├── __init__.py
│   ├── client.py                 # Existing OpenAI client
│   └── openai_agent.py           # OpenAI-specific agent
├── web_search/
│   ├── __init__.py
│   ├── duckduckgo_client.py      # DuckDuckGo XML API client
│   ├── search_tool.py            # Pydantic-ai tool definition
│   └── models.py                 # Search result models
├── agents/
│   ├── __init__.py
│   ├── base_agent.py             # Abstract agent interface
│   └── agent_factory.py          # Agent creation factory
└── __init__.py
```

## Implementation Steps

### Phase 1: Core Infrastructure

#### Step 1.1: DuckDuckGo XML API Client
- **File**: `integrations/web_search/duckduckgo_client.py`
- **Purpose**: Handle DuckDuckGo XML API requests
- **Features**:
  - XML response parsing
  - Error handling and retries
  - Rate limiting
  - Result formatting

#### Step 1.2: Search Result Models
- **File**: `integrations/web_search/models.py`
- **Purpose**: Pydantic models for search results
- **Models**:
  - `SearchResult`: Individual search result
  - `SearchResponse`: Complete search response
  - `SearchRequest`: Search query parameters

#### Step 1.3: Pydantic-AI Tool Definition
- **File**: `integrations/web_search/search_tool.py`
- **Purpose**: Define web search tool for pydantic-ai
- **Features**:
  - Tool schema definition
  - Input/output validation
  - Error handling
  - Result formatting

### Phase 2: AI Integration Layer

#### Step 2.1: Ollama Client Implementation
- **File**: `integrations/ollama/ollama_client.py`
- **Purpose**: Complete Ollama client with pydantic-ai support
- **Features**:
  - Async/sync client methods
  - Model management
  - Tool calling support
  - Error handling

#### Step 2.2: Abstract Agent Interface
- **File**: `integrations/agents/base_agent.py`
- **Purpose**: Define common agent interface
- **Features**:
  - Abstract base class
  - Common methods (chat, tool calling)
  - Configuration interface

#### Step 2.3: OpenAI Agent Implementation
- **File**: `integrations/openai/openai_agent.py`
- **Purpose**: OpenAI-specific agent implementation
- **Features**:
  - OpenAI tool calling
  - Message handling
  - Response processing

#### Step 2.4: Ollama Agent Implementation
- **File**: `integrations/ollama/ollama_agent.py`
- **Purpose**: Ollama-specific agent implementation
- **Features**:
  - Ollama tool calling
  - Message handling
  - Response processing

### Phase 3: Agent Factory and Configuration

#### Step 3.1: Agent Factory
- **File**: `integrations/agents/agent_factory.py`
- **Purpose**: Create agents based on configuration
- **Features**:
  - Factory pattern implementation
  - Configuration validation
  - Easy provider switching

#### Step 3.2: Configuration System
- **File**: `integrations/config.py`
- **Purpose**: Centralized configuration management
- **Features**:
  - Environment-based configuration
  - Provider selection
  - Model configuration

### Phase 4: Integration and Testing

#### Step 4.1: Package Integration
- **File**: `integrations/__init__.py`
- **Purpose**: Export all components
- **Features**:
  - Clean public API
  - Import convenience functions
  - Type hints

#### Step 4.2: Example Usage
- **File**: `examples/web_search_example.py`
- **Purpose**: Demonstrate usage
- **Features**:
  - OpenAI example
  - Ollama example
  - Configuration switching

## Dependencies to Add

### New Dependencies
```txt
# Web search and XML parsing
requests>=2.31.0
lxml>=4.9.0
beautifulsoup4>=4.12.0

# Pydantic-ai for tool definitions
pydantic-ai>=0.1.0

# Ollama client
ollama>=0.1.0

# Additional utilities
aiohttp>=3.9.0
```

## Configuration Examples

### Environment Variables
```bash
# AI Provider Selection
AI_PROVIDER=openai  # or "ollama"

# OpenAI Configuration
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4-turbo

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

### Usage Examples

#### Basic Web Search
```python
from integrations import create_agent, WebSearchTool

# Create agent with web search tool
agent = create_agent(
    provider="openai",  # or "ollama"
    tools=[WebSearchTool()]
)

# Search the web
response = await agent.chat("Search for latest AI news")
```

#### Switching Providers
```python
from integrations import AgentFactory

# Switch between providers
openai_agent = AgentFactory.create("openai")
ollama_agent = AgentFactory.create("ollama")

# Both agents have the same interface
results = await openai_agent.search("Python programming")
results = await ollama_agent.search("Python programming")
```

## Testing Strategy

### Unit Tests
- DuckDuckGo client tests
- Search tool tests
- Agent interface tests
- Configuration tests

### Integration Tests
- End-to-end search workflow
- Provider switching tests
- Error handling tests

### Mock Tests
- API response mocking
- Network error simulation
- Rate limiting tests

## Error Handling

### Network Errors
- Retry logic with exponential backoff
- Timeout handling
- Connection error recovery

### API Errors
- DuckDuckGo API error handling
- OpenAI/Ollama API error handling
- Rate limit handling

### Validation Errors
- Input validation
- Response validation
- Tool parameter validation

## Performance Considerations

### Caching
- Search result caching
- Model response caching
- Configuration caching

### Rate Limiting
- DuckDuckGo API rate limiting
- AI provider rate limiting
- Request queuing

### Async Support
- Async client implementations
- Concurrent request handling
- Background processing

## Security Considerations

### API Key Management
- Environment variable usage
- Secure key storage
- Key rotation support

### Input Validation
- Query sanitization
- URL validation
- Content filtering

### Error Information
- Safe error messages
- No sensitive data exposure
- Audit logging

## Future Enhancements

### Additional Search Providers
- Google Custom Search API
- Bing Search API
- SerpAPI integration

### Advanced Features
- Search result summarization
- Multi-language support
- Image search support
- News search filtering

### Monitoring and Analytics
- Usage metrics
- Performance monitoring
- Error tracking
- Cost tracking

## Implementation Timeline

### Week 1: Core Infrastructure
- DuckDuckGo client
- Search models
- Basic tool definition

### Week 2: AI Integration
- Ollama client completion
- Agent interfaces
- Basic agent implementations

### Week 3: Integration and Testing
- Agent factory
- Configuration system
- Unit tests

### Week 4: Polish and Documentation
- Integration tests
- Examples
- Documentation
- Performance optimization

## Success Criteria

### Functional Requirements
- ✅ Web search tool works with DuckDuckGo
- ✅ Pydantic-ai tool definition complete
- ✅ OpenAI integration functional
- ✅ Ollama integration functional
- ✅ Easy provider switching
- ✅ Error handling robust

### Non-Functional Requirements
- ✅ Type safety throughout
- ✅ Async support
- ✅ Comprehensive testing
- ✅ Good documentation
- ✅ Performance acceptable
- ✅ Security considerations met
