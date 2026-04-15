import os

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    pass

SYSTEM_PROMPT = """
Bạn là chuyên viên tư vấn mua sắm của hệ thống thương mại điện tử.
QUY TẮC:
1. Chỉ gợi ý sản phẩm dựa trên thông tin được cung cấp
2. Không tự ý thay đổi giá, thông tin sản phẩm
3. Trả lời bằng tiếng Việt, thân thiện và ngắn gọn
4. Xưng "em", gọi khách là "anh/chị"
"""

class MockLLM:
    def invoke(self, messages):
        class Content:
            content = "Dạ, em xin gợi ý cho anh/chị sản phẩm phù hợp. Hiện tại hệ thống đang chạy ở chế độ giả lập vì thiếu API KEY."
        return Content()

def get_answer(user_question, context_docs, user_profile=None, conversation_history=None):
    context_text = "\n\n---\n\n".join([doc.page_content for doc in context_docs]) if context_docs else "Không có sản phẩm nào phù hợp trong CSDL."
    
    profile_text = ""
    if user_profile:
        profile_text = f"""
        === THÔNG TIN NGƯỜI DÙNG ===
        - Phân khúc: {user_profile.get('segment_name', 'unknown')}
        """
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    
    if conversation_history:
        messages.extend(conversation_history)
        
    user_prompt = f"""
    {profile_text}
    
    === THÔNG TIN SẢN PHẨM THAM KHẢO ===
    {context_text}
    
    === CÂU HỎI CỦA KHÁCH HÀNG ===
    {user_question}
    
    Hãy tư vấn dựa trên context.
    """
    
    messages.append({"role": "user", "content": user_prompt})
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        llm = ChatGoogleGenerativeAI(
            model='gemini-2.5-flash',
            temperature=0.3,
            google_api_key=api_key
        )
        # Convert dictionary format to tuple format expected by LangChain messages
        formatted_messages = [(m["role"], m["content"]) for m in messages]
        response = llm.invoke(formatted_messages)
        return response.content
    else:
        return MockLLM().invoke(messages).content
