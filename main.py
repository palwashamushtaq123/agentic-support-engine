import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from langgraph.types import Command

# Load environment variables from .env file
load_dotenv()

# Verify API key exists
if not os.getenv("GROQ_API_KEY"):
    print("WARNING: GROQ_API_KEY is missing from environment variables!")

from database import seed_db
from graph import graph

app = FastAPI(title="LangGraph Refund Support Agent")

class ChatMessage(BaseModel):
    message: str
    thread_id: str = "default_thread"

class ReviewPayload(BaseModel):
    approved: bool

@app.on_event("startup")
def startup_event():
    print("Starting LangGraph Refund Agent......")
    seed_db()  # Ensures database.csv is populated on startup

@app.get("/")
async def read_index():
    # Serves the frontend UI
    return FileResponse("index.html")

@app.post("/support")
async def support(payload: ChatMessage):
    try:
        config = {"configurable": {"thread_id": payload.thread_id}}
        
        # Check if graph is already waiting at an interrupt for this thread
        current_state = graph.get_state(config)
        if current_state.next and "human_review" in current_state.next:
            interrupts = [task.interrupts[0].value for task in current_state.tasks if task.interrupts]
            return {
                "status": "awaiting_approval",
                "thread_id": payload.thread_id,
                "interrupts": interrupts,
                "response": "Awaiting manager approval for this high-value refund."
            }

        # Invoke the LangGraph workflow
        result = graph.invoke(
            {"message": payload.message, "request_id": f"REQ-{payload.thread_id}"}, 
            config=config
        )
        
        # Check if the execution hit an interrupt during this invocation
        state_after = graph.get_state(config)
        if state_after.next and "human_review" in state_after.next:
            interrupts = [task.interrupts[0].value for task in state_after.tasks if task.interrupts]
            return {
                "status": "awaiting_approval",
                "thread_id": payload.thread_id,
                "interrupts": interrupts,
                "response": "Your refund request exceeds $100 and requires human approval."
            }

        return {
            "status": "success",
            "thread_id": payload.thread_id,
            "response": result.get("response", "No reply generated."),
            "intent": result.get("intent", ""),
            "order_id": result.get("order_id", ""),
            "outcome": result.get("outcome", "")
        }
    except Exception as e:
        print(f"Error executing graph: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "response": f"Internal Server Error: {str(e)}"
        }

@app.post("/review/{thread_id}")
async def review_refund(thread_id: str, payload: ReviewPayload):
    try:
        config = {"configurable": {"thread_id": thread_id}}
        
        # Resume the interrupted graph using LangGraph Command
        result = graph.invoke(
            Command(resume={"approved": payload.approved}),
            config=config
        )
        
        return {
            "status": "success",
            "thread_id": thread_id,
            "response": result.get("response", "Review processed and refund finalized."),
            "intent": result.get("intent", ""),
            "order_id": result.get("order_id", ""),
            "outcome": result.get("outcome", "")
        }
    except Exception as e:
        print(f"Error resuming graph during review: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "response": f"Internal Server Error during review: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)