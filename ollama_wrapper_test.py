# Example usage
from ollama_wrapper import OllamaWrapper

# Initialize the wrapper
ollama = OllamaWrapper(base_url='http://localhost:8080')

# Generate text
response = ollama.generate_text("Once upon a time, in a land far, far away...")
print(response['generated_text'])

# Tokenize text
tokens = ollama.tokenize_text("Hello, world!")
print(tokens)

# Detokenize text
detokenized_text = ollama.detokenize_text([7, 23, 12])
print(detokenized_text)