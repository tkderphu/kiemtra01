import numpy as np
import redis
import json
import torch
import os
from .transformer_model import BehaviorTransformer, Config

class BehaviorPredictor:
    def __init__(self, model_path='behavior_model.pt'):
        # Instantiate model directly to bypass needing weights initially, but try to load if exists.
        self.model = BehaviorTransformer(Config())
        try:
            if os.path.exists(model_path):
                self.model.load_state_dict(torch.load(model_path, map_location='cpu'))
                print("Model weights loaded.")
            else:
                print("Weights not found, using uninitialized model.")
        except Exception as e:
            print(f"Error loading model: {e}")
        self.model.eval()
        
        self.redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
        
        self.action_to_id = {
            'view': 0, 'click': 1, 'add_to_cart': 2, 'remove_from_cart': 3,
            'purchase': 4, 'search': 5, 'filter': 6, 'share': 7,
            'write_review': 8, 'add_to_wishlist': 9
        }
        self.segment_names = ['price_sensitive', 'brand_loyal', 'impulsive', 'window_shopper']
    
    def predict(self, user_id, session_id, recent_actions):
        try:
            # Check cache
            cache_key = f"behavior:{user_id}:{session_id}"
            cached = self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception:
            # Fallback if Redis is down
            pass
            
        actions, product_ids, time_deltas, mask = self._prepare_sequence(recent_actions)
        user_meta = self._get_user_metadata(user_id)
        
        with torch.no_grad():
            outputs = self.model(actions, product_ids, time_deltas, user_meta, mask)
        
        segment = int(torch.argmax(outputs['segment_logits']))
        response = {
            'user_embedding': outputs['user_embedding'].tolist()[0],
            'segment': segment,
            'segment_name': self.segment_names[segment],
            'churn_risk': float(outputs['churn_probability'][0]),
            'predicted_ltv': float(outputs['ltv_prediction'][0]),
            'next_most_likely_action': self._get_action_name(torch.argmax(outputs['next_action_logits']))
        }
        
        try:
            # Cache for 10 minutes
            self.redis_client.setex(cache_key, 600, json.dumps(response))
        except Exception:
            pass
        return response
    
    def _prepare_sequence(self, recent_actions, seq_len=50):
        # Dummy Implementation
        actions = torch.zeros((1, seq_len), dtype=torch.long)
        product_ids = torch.zeros((1, seq_len), dtype=torch.long)
        time_deltas = torch.zeros((1, seq_len, 1), dtype=torch.float)
        mask = torch.ones((1, seq_len), dtype=torch.bool)
        return actions, product_ids, time_deltas, mask

    def _get_user_metadata(self, user_id):
        return torch.zeros((1, 32), dtype=torch.float)

    def _get_action_name(self, action_id):
        id_to_action = {v: k for k, v in self.action_to_id.items()}
        return id_to_action.get(int(action_id), 'view')
