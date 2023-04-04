import math
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class Transformer(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, num_heads):
        super(Transformer, self).__init__()
        
        # Parameters for the self-attention mechanism
        self.num_heads = num_heads
        self.head_dim = hidden_dim // num_heads
        
        # Input embedding layer. This layer takes the tokenised input integers and converts them to tensors of a fixed size
        self.embedding = nn.Embedding(input_dim, hidden_dim)
        
        # Encoder layers
        self.encoder_layers = nn.ModuleList([
            nn.TransformerEncoderLayer(d_model=hidden_dim, nhead=num_heads)
            for _ in range(num_layers)
        ])
        
        # Decoder layers
        self.decoder_layers = nn.ModuleList([
            nn.TransformerDecoderLayer(d_model=hidden_dim, nhead=num_heads)
            for _ in range(num_layers)
        ])
        
        # Output linear layer
        self.linear = nn.Linear(hidden_dim, input_dim)
        
    def forward(self, src, tgt, src_mask=None, tgt_mask=None):
        # Embed the source and target sequences
        src_embed = self.embedding(src)
        tgt_embed = self.embedding(tgt)
        
        # Add the positional encoding matrix to the input embeddings
        src_pos = positional_encoding(src_embed)
        tgt_pos = positional_encoding(tgt_embed)
        
        # Run the source sequence through the encoder layers
        encoder_output = src_pos
        for encoder_layer in self.encoder_layers:
            encoder_output = encoder_layer(encoder_output, src_mask=src_mask)
        
        # Run the target sequence through the decoder layers with self-attention mechanism
        decoder_output = tgt_pos
        for decoder_layer in self.decoder_layers:
            decoder_output = decoder_layer(
                tgt=decoder_output, 
                memory=encoder_output, 
                tgt_mask=tgt_mask, 
                memory_mask=src_mask
            )
        
        # Linear layer to generate output predictions
        output = self.linear(decoder_output)
        return output
    
def positional_encoding(x):
    # Create a positional encoding matrix
    seq_len, hidden_dim = x.shape[1], x.shape[2]
    pos_enc = torch.zeros(seq_len, hidden_dim)
    pos = torch.arange(0, seq_len, dtype=torch.float).unsqueeze(1)
    div_term = torch.exp(torch.arange(0, hidden_dim, 2).float() * (-math.log(10000.0) / hidden_dim))
    pos_enc[:, 0::2] = torch.sin(pos * div_term)
    pos_enc[:, 1::2] = torch.cos(pos * div_term)
    
    # Add the positional encoding matrix to the input embeddings
    x = x + pos_enc.unsqueeze(0)
    return x

def create_mask(x, pad_token=0):
    # Create a mask to prevent attention to padding tokens and future tokens
    mask = (x != pad_token).unsqueeze(1).unsqueeze(2)
    seq_len = x.shape[1]
    future_mask = torch.tril(torch.ones(seq_len, seq_len)).unsqueeze(0)
    mask = mask & future_mask
    return mask.to(x.device)

