import torch
from transformers import BertTokenizer, BertModel

# Step 1: Tokenization
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
text = "Hello, how are you?"
tokens = tokenizer(text, return_tensors='pt')

# Step 2: Embedding and Encoding
model = BertModel.from_pretrained('bert-base-uncased')
embeddings = model(**tokens)

# The embeddings contain the contextual representation of the input text
print(embeddings.last_hidden_state)