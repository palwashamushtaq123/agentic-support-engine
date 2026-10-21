import os
import re
from langchain_groq import ChatGroq
from schemas import Classification


def llm():
    # Automatically tries active models and prints the picked one
    models = [
        os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant'),
        'mixtral-8x7b-32768',
        'llama3-70b-8192'
    ]
    
    for model_name in models:
        try:
            chat = ChatGroq(model=model_name, temperature=0)
            print(f"--> Active Model Picked: {model_name}")
            return chat
        except Exception as e:
            continue
            
    return ChatGroq(model="mixtral-8x7b-32768", temperature=0)


def classify(message: str) -> dict:
    try:
        result = llm().with_structured_output(Classification).invoke([
            ('system', 'Classify the customer support request. Extract an order ID like ORD-1001 if present. Never invent an ID.'),
            ('human', message),
        ])
    except Exception:
        class FallbackClass:
            intent = "refund" if "refund" in message.lower() else "general"
            order_id = None
        result = FallbackClass()
        
    match = re.search(r'\bORD-\d+\b', message, re.IGNORECASE)
    return {
        'intent': getattr(result, 'intent', 'general'), 
        'order_id': match.group(0).upper() if match else getattr(result, 'order_id', None)
    }


def compose_reply(message: str, outcome: str, detail: str) -> str:
    try:
        response = llm().invoke([
            ('system', 'Write a concise, courteous customer service reply. The outcome and detail are authoritative. Never say a payment was sent or money returned when only a demo ledger was updated. Never override the decision.'),
            ('human', f'Customer: {message}\nOutcome: {outcome}\nDetail: {detail}'),
        ])
        return response.content if isinstance(response.content, str) else str(response.content)
    except Exception as e:
        return f"Hello! Regarding your request, {detail}"