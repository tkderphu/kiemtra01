import torch
import torch.nn as nn
import torch.nn.functional as F

class Config:
    d_model = 256

class BehaviorTransformer(nn.Module):
    def __init__(self, config=Config()):
        super().__init__()
        self.config = config
        
        # Embedding layers
        self.action_embedding = nn.Embedding(15, config.d_model)  # 15 action types
        self.product_embedding = nn.Embedding(500001, config.d_model)  # product_id 0-500k
        self.time_embedding = nn.Linear(1, config.d_model)
        self.position_embedding = nn.Embedding(50, config.d_model)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=256, nhead=8, dim_feedforward=1024,
            dropout=0.1, activation='gelu', batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=4)
        
        # User metadata projection
        self.user_meta_proj = nn.Linear(32, 256)
        
        # Task heads
        self.embedding_proj = nn.Linear(256, 128)
        self.segment_head = nn.Linear(128, 4)
        self.next_action_head = nn.Linear(128, 15)
        self.churn_head = nn.Linear(128, 1)
        self.ltv_head = nn.Linear(128, 1)
        
    def forward(self, actions, product_ids, time_deltas, user_metadata, mask):
        batch, seq_len = actions.shape
        
        # Positional encoding
        positions = torch.arange(seq_len, device=actions.device).unsqueeze(0)
        pos_embed = self.position_embedding(positions)
        
        # Token embeddings
        action_embed = self.action_embedding(actions)
        product_embed = self.product_embedding(product_ids)
        time_embed = self.time_embedding(time_deltas)
        
        # Combine
        token_embed = action_embed + product_embed + time_embed + pos_embed
        
        # Transformer
        transformer_mask = ~mask
        output = self.transformer(token_embed, src_key_padding_mask=transformer_mask)
        
        # Take last valid token
        last_indices = mask.sum(dim=1) - 1
        last_output = output[torch.arange(batch), last_indices]
        
        # Fuse with user metadata
        user_meta_proj = self.user_meta_proj(user_metadata)
        fused = last_output + user_meta_proj
        
        # User embedding
        user_embedding = F.normalize(self.embedding_proj(fused), p=2, dim=1)
        
        return {
            'user_embedding': user_embedding,
            'segment_logits': self.segment_head(user_embedding),
            'next_action_logits': self.next_action_head(user_embedding),
            'churn_probability': torch.sigmoid(self.churn_head(user_embedding)),
            'ltv_prediction': F.relu(self.ltv_head(user_embedding))
        }
