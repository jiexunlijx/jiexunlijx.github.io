# Importing the required modules
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
from torch.utils.data import DataLoader

# Defining the SwiGLU activation function with learnable beta parameter
# The rest of the SwiGLU implementation is in the TransformerEncoder class
# SwiGLU is smoother than ReLU, which can lead to better optimization and faster convergence.
# SwiGLU is non-monotonic, which allows it to capture complex non-linear relationships between inputs and outputs.
# SwiGLU uses a gating mechanism, which allows it to selectively activate neurons based on the input it receives. This can help to reduce overfitting and improve generalization.
# Swiglu allows a small number of negative weights to be propagated through, while ReLU thresholds all negative weights to zero . This can help with gradient flow and avoid the dying ReLU problem.  
def swiglu(x, y, beta):
    return x * F.sigmoid(beta * y)

# Defining the RMSNorm layer
class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-8):
        super().__init__()
        self.dim = dim
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))
        self.bias = nn.Parameter(torch.zeros(dim))

    def forward(self, x):
        mean = x.mean(-1, keepdim=True)
        std = x.std(-1, keepdim=True)
        return self.weight * (x - mean) / (std + self.eps) + self.bias

# Defining the Rotary Positional Embedding layer
# rotational encoding is that it is more expressive than sinusoidal encoding, which is limited by its periodic nature. 
# Rotational encoding can represent arbitrary positions in the sequence and is not restricted to a fixed set of frequencies. 
# This allows the transformer to better capture the relative positions of tokens in the sequence.
# Rotational encoding can be applied to sequences of any length without requiring retraining. 
# This makes it a more flexible and scalable method for encoding positional information.
class RotaryEmbedding(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim
        inv_freq = 1. / (10000 ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer('inv_freq', inv_freq)

    def forward(self, x):
        seq_len = x.shape[1]
        t = torch.arange(seq_len).type_as(self.inv_freq)
        freqs = torch.einsum('i,j->ij', t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1).to(x.device)
        return emb[None, :, :]

# Defining the Transformer Encoder layer
class TransformerEncoder(nn.Module):
    def __init__(self, dim, heads, mlp_dim):
        super().__init__()
        self.dim = dim
        self.heads = heads
        self.mlp_dim = mlp_dim

        # Pre-normalization layers
        self.norm1 = RMSNorm(dim)
        self.norm2 = RMSNorm(dim)

        # Self-attention layer with rotary embeddings
        self.attn = nn.MultiheadAttention(dim, heads)
        self.rotary_emb = RotaryEmbedding(dim // 2)

        # Feed-forward layer with SwiGLU activation
        self.ffn = nn.Sequential(
            nn.Linear(dim, mlp_dim * 4),
            nn.Linear(mlp_dim * 4, mlp_dim * 4),
            lambda x: swiglu(x[:, :, :mlp_dim * 2], x[:, :, mlp_dim * 2:], self.beta),
            nn.Linear(mlp_dim * 2, dim),
        )
        self.beta = nn.Parameter(torch.ones(1))

    def forward(self, x):
        # Adding rotary embeddings to the input
        pos_emb = self.rotary_emb(x)
        x = x + pos_emb

        # Applying pre-normalization and self-attention
        x = x + self.attn(self.norm1(x), self.norm1(x), self.norm1(x))[0]

        # Applying pre-normalization and feed-forward
        x = x + self.ffn(self.norm2(x))

        return x

# Defining the Transformer Encoder module
class Transformer(nn.Module):
    def __init__(self, vocab_size, dim, depth, heads, mlp_dim):
        super().__init__()
        self.vocab_size = vocab_size
        self.dim = dim
        self.depth = depth

        # Embedding layer for tokens
        self.embed = nn.Embedding(vocab_size, dim)

        # Encoder layers
        self.layers = nn.ModuleList([])
        for _ in range(depth):
            self.layers.append(TransformerEncoder(dim, heads, mlp_dim))

    def forward(self, x):
        # Getting the token embeddings
        x = self.embed(x)

        # Applying the encoder layers
        for layer in self.layers:
            x = layer(x)

        return x

# Defining the model hyperparameters based on Table 2 in the document
vocab_size = 50257 # GPT-2 vocabulary size
dim = 4096 # Model dimension for LLaMA-7B model
depth = 32 # Number of encoder layers for LLaMA-7B model
heads = 32 # Number of attention heads for LLaMA-7B model
mlp_dim = 10240 # Feed-forward dimension for LLaMA-7B model

# Creating the model instance
model = Transformer(vocab_size, dim, depth, heads, mlp_dim)

# params, dimension, n heads, n layers, learning rate, batch size, n tokens
# 6.7B 4096 32 32 3.0e−4 4M 1.0T
# 13.0B 5120 40 40 3.0e−4 4M 1.0T
# 32.5B 6656 52 60 1.5e−4 4M 1.4T
# 65.2B 8192 64 80 1.5e−4 4M 1.4T

# Defining the optimizer hyperparameters
lr = 0.0006 # Learning rate for LLaMA-7B model
wd = 0.1 # Weight decay
gc = 1.0 # Gradient clipping
bs = 4096 # Batch size for LLaMA-7B model

# Creating the optimizer instance
optimizer = AdamW(model.parameters(), lr=lr, weight_decay=wd)

# Defining the learning rate scheduler
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=bs, eta_min=lr * 0.1)

# Defining the device (attmepting to use GPU if available)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Defining the training loop
def train(model, optimizer, scheduler, dataloader, epochs):
    # Setting the model to training mode
    model.train()

    # Looping over the epochs
    for epoch in range(epochs):
        # Initializing the epoch loss
        epoch_loss = 0

        # Looping over the batches
        for batch in dataloader:
            # Getting the input and target tokens
            input_ids = batch['input_ids']
            target_ids = batch['target_ids']

            # Moving the tensors to the device
            input_ids = input_ids.to(device)
            target_ids = target_ids.to(device)

            # Forward pass through the model
            output = model(input_ids)

            # Calculating the loss
            loss = F.cross_entropy(output.view(-1, vocab_size), target_ids.view(-1))

            # Backward pass and optimization
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), gc)
            optimizer.step()
            scheduler.step()

            # Updating the epoch loss
            epoch_loss += loss.item()

        # Printing the average epoch loss
        print(f'Epoch {epoch + 1}, Loss: {epoch_loss / len(dataloader)}')