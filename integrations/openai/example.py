"""
Example usage of the OpenAI integration client.

This file demonstrates how to use the OpenAI client for various tasks.
Make sure to set your OPENAI_API_KEY in your .env file before running.
"""

import asyncio
from integrations.openai import OpenAIClient, create_openai_client


def basic_chat_example():
    """Example of basic chat completion."""
    print("=== Basic Chat Example ===")

    # Create client (will load API key from .env)
    client = create_openai_client()

    # Simple chat
    response = client.simple_chat(
        "Hello! Can you explain what machine learning is in simple terms?"
    )
    print(f"Response: {response}")


def advanced_chat_example():
    """Example of advanced chat completion with conversation history."""
    print("\n=== Advanced Chat Example ===")

    client = OpenAIClient()

    # Multi-turn conversation
    messages = [
        {"role": "system", "content": "You are a helpful Python programming assistant."},
        {"role": "user", "content": "How do I create a list in Python?"},
        {"role": "assistant", "content": "You can create a list in Python using square brackets: my_list = [1, 2, 3, 'hello']"},
        {"role": "user", "content": "How do I add an item to this list?"}
    ]

    response = client.chat_completion(
        messages=messages,
        model="gpt-3.5-turbo",
        temperature=0.3,
        max_tokens=150
    )

    print(f"Response: {response.choices[0].message.content}")


def completion_example():
    """Example of text completion."""
    print("\n=== Text Completion Example ===")

    client = OpenAIClient()

    prompt = "The benefits of using Python for data science include:"
    response = client.simple_complete(prompt)
    print(f"Completion: {response}")


def embedding_example():
    """Example of creating embeddings."""
    print("\n=== Embedding Example ===")

    client = OpenAIClient()

    # Single text embedding
    text = "Machine learning is a subset of artificial intelligence."
    embedding = client.get_embedding_vector(text)
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")

    # Multiple texts
    texts = [
        "Python is a programming language",
        "Machine learning uses algorithms",
        "Data science involves statistics"
    ]

    response = client.create_embeddings(texts)
    print(f"Created embeddings for {len(response.data)} texts")


async def async_chat_example():
    """Example of async chat completion."""
    print("\n=== Async Chat Example ===")

    client = OpenAIClient()

    messages = [
        {"role": "user", "content": "What's the weather like?"}
    ]

    response = await client.async_chat_completion(messages)
    print(f"Async response: {response.choices[0].message.content}")


def list_models_example():
    """Example of listing available models."""
    print("\n=== Available Models Example ===")

    client = OpenAIClient()

    try:
        models = client.list_models()
        print(f"Available models ({len(models)}):")
        # Show first 10 models
        for model in sorted(models)[:10]:
            print(f"  - {model}")
        if len(models) > 10:
            print(f"  ... and {len(models) - 10} more")
    except Exception as e:
        print(f"Error listing models: {e}")


def main():
    """Run all examples."""
    print("OpenAI Integration Examples")
    print("=" * 50)

    try:
        # Basic examples
        basic_chat_example()
        advanced_chat_example()
        completion_example()
        embedding_example()
        list_models_example()

        # Async example
        print("\n=== Running Async Example ===")
        asyncio.run(async_chat_example())

    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nPlease make sure to:")
        print("1. Create a .env file in your project root")
        print("2. Add your OpenAI API key: OPENAI_API_KEY=your_key_here")
        print("3. Install required dependencies: pip install -r requirements.txt")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()