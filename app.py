from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import json
import os
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types
from dotenv import load_dotenv

# NOTE: Ensure these imports exist in your environment
# from google.adk.tools import google_search
# from google.adk.memory import preload_memory, auto_save_to_memory

load_dotenv()

# Global
runner = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global runner

    # 1. Input Collector
    input_collector = Agent(
        name="input_collector",
        model=Gemini(model_name="gemini-1.5-flash"),
        description="Collects user preferences for mess meal planning.",
        instruction="""
        Ask the user step-by-step:
        - How many people? (default 4)
        - Weekly budget per person? (default ₹400)
        - Max non-veg times a week? (0–14)
        - Preferred non-veg: chicken, egg, fish, mutton
        - Favourite veg dishes
        - Any dish you HATE?
        - Jain / allergies?
        - Breakfast from mess fund?
        Also ask:
        - Goal
        - Health conditions
        - Activity level
        Return clean JSON.
        """
    )

    # 2. Constraint Validator
    validator = Agent(
        name="constraint_validator",
        model=Gemini(model_name="gemini-1.5-flash"),
        description="Applies hard mess rules + user rules.",
        instruction="""
        Hard rules (₹400/person, 4 people):
        - Adjust non-veg if over budget
        - Only 1 non-veg meal/day
        - No paneer if budget ≤ ₹400
        - Weekdays cooking ≤60 min
        - Sunday = special
        - Breakfast 4–5 days allowed
        Validate and return JSON.
        """
    )

    # 3. Meal Planner
    planner = Agent(
        name="meal_planner",
        model=Gemini(model_name="gemini-1.5-flash"),
        description="Generates full 7-day mess menu.",
        instruction="""
        Create a 7-day 2-course meal plan.
        - Plan 14 meals, not daywise
        - Sunday special
        - Lunch must include rice
        - Chicken/fish at least once/week
        - No consecutive identical meals
        - Stay in budget, use leftovers
        Return markdown table + cost.
        """
    )

    # Feedback Agent
    feedback_agent = Agent(
        name="feedback",
        model=Gemini(model_name="gemini-1.5-flash"),
        instruction="Ask for rating (1-5) and what changes are needed. Return JSON."
    )


    budget_agent = Agent(
        name="budget_estimator",
        model=Gemini(model_name="gemini-1.5-flash"),
        description="Real-time grocery prices using Google search",
        instruction="""
        Use Google Search to find ingredient prices.
        Compute exact weekly cost.
        Suggest cheaper alternatives.
        Return final menu + cost.
        """,
        tools=[google_search]
    )
    async def auto_save_session_to_memory_callback(callback_context):
        await callback_context._invocation_context.memory_service.add_session_to_memory(
            callback_context._invocation_context.session)

    # Root agent
    root_agent = Agent(
        name="MessMealPlanner",
        model=Gemini(model_name="gemini-1.5-flash"),
        description="Full Indian mess meal planner",
        instruction="Run in order: input_collector → constraint_validator → meal_planner.",
        tools=[PreloadMemoryTool()],
        after_agent_callback=auto_save_session_to_memory_callback,
        sub_agents=[input_collector, validator, planner, feedback_agent]
    )

    runner = InMemoryRunner(agent=root_agent, app_name="mess_planner")
    print("✅ Root Agent & Runner initialized.")

    yield

    print("🛑 Shutting down.")


app = FastAPI(title="Desi Mess Meal Planner", lifespan=lifespan)


@app.post("/plan")
async def plan(request: Request):
    data = await request.json()
    message = data.get("message", "Plan kar do bhai")
    
    content = types.Content(role='user', parts=[types.Part(text=message)])
    response = ""
    
    try:
        # Explicit session create first (error fix)
        session = await runner.session_service.create_session(
            app_name="mess_planner",
            user_id="user1",
            session_id="session1"
        )
        
        # Now run_async (no create_if_missing needed)
        async for event in runner.run_async(
            user_id="user1",
            session_id="session1",
            new_message=content
        ):
            if event.is_final_response() and event.content:
                response = "".join(p.text for p in event.content.parts if p.text)
                break
    except Exception as e:
        return {"error": str(e)}
    
    return {"plan": response or "Thinking... 10 sec mein plan ready"}


@app.get("/")
def home():
    return {"message": "Desi Mess Planner LIVE – POST to /plan"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
