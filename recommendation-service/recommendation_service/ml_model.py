import pandas as pd
from sklearn.decomposition import TruncatedSVD
import numpy as np
from .models import Interaction, Recommendation
from django.db.models import Sum

_last_train_count = 0

def train_model():
    """
    Background Task: Huấn luyện AI Model bằng Matrix Factorization 
    và lưu kết quả dự đoán vào Database PostgreSQL.
    """
    global _last_train_count
    
    interactions = Interaction.objects.values('user_id', 'product_id').annotate(total_weight=Sum('weight'))
    current_count = interactions.count()
    
    if current_count == 0 or current_count == _last_train_count:
        return # Skip training if no new data
        
    df = pd.DataFrame(list(interactions))
    if df.empty or len(df['user_id'].unique()) < 2 or len(df['product_id'].unique()) < 2:
        return 
        
    user_item_matrix = df.pivot(index='user_id', columns='product_id', values='total_weight').fillna(0)
    
    n_components = min(5, len(user_item_matrix.columns) - 1, len(user_item_matrix) - 1)
    if n_components < 1: n_components = 1
        
    svd = TruncatedSVD(n_components=n_components)
    matrix_factorized = svd.fit_transform(user_item_matrix)
    
    predicted_ratings = np.dot(matrix_factorized, svd.components_)
    predicted_df = pd.DataFrame(predicted_ratings, index=user_item_matrix.index, columns=user_item_matrix.columns)
    
    for user_id in predicted_df.index:
        user_history = df[df['user_id'] == user_id]['product_id'].tolist()
        user_preds = predicted_df.loc[user_id].sort_values(ascending=False)
        recs = [pid for pid in user_preds.index if pid not in user_history]
        
        top_5_ids = [int(x) for x in recs[:5]]
        
        # Save to PostgreSQL
        Recommendation.objects.update_or_create(
            user_id=user_id,
            defaults={'product_ids': top_5_ids}
        )
        
    _last_train_count = current_count
    print("✅ [BACKGROUND TASK] Đã retrain thành công AI Model và lưu Database!")

def get_ml_recommendations(user_id):
    # Trích xuất ngay lập tức từ Database (siêu nhanh, O(1))
    rec = Recommendation.objects.filter(user_id=user_id).first()
    if rec and rec.product_ids:
        return rec.product_ids
        
    # Người dùng mới chưa có data -> Trả về rỗng để Frontend ẩn mục gợi ý
    return []
