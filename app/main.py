# Import Python's built-in os module
# This helps us read environment variables like OPENAI_API_KEY
import os

# Import FastAPI core class used to create the web application
from fastapi import FastAPI, Form, Request

# HTMLResponse is used to return HTML pages
# JSONResponse is used to return structured JSON responses
from fastapi.responses import HTMLResponse, JSONResponse

# StaticFiles allows serving static files like CSS, JS, images
from fastapi.staticfiles import StaticFiles

# Jinja2Templates allows rendering HTML templates dynamically
from fastapi.templating import Jinja2Templates

# dotenv helps load environment variables from a .env file
from dotenv import load_dotenv

# OpenAI client library used to call OpenAI APIs
from openai import OpenAI

# Import the calculate function from calculator.py
# This function performs add, subtract, multiply, divide operations
from app.calculator import calculate


# Load environment variables from the .env file
# This will load OPENAI_API_KEY into the system environment
load_dotenv()


# Create a FastAPI application instance
# This is the main app object used to define API routes
app = FastAPI()


# Mount the "static" directory so the app can serve CSS and JS files
# Example: /static/style.css will map to the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")


# Configure Jinja2 template engine
# This tells FastAPI where HTML templates are stored
templates = Jinja2Templates(directory="app/templates")


# Create an OpenAI client
# The API key is read securely from environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Define a GET endpoint for the home page "/"
# response_class=HTMLResponse means this endpoint returns HTML
@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    # Render index.html from the templates folder
    # "request" must be passed so the template engine can access request info
    return templates.TemplateResponse("index.html", {"request": request})


# Define an API endpoint to perform calculations
# This endpoint accepts POST requests at /calculate
@app.post("/calculate")
def calculate_api(

    # num1 is received from an HTML form field
    num1: float = Form(...),

    # num2 is also received from the form
    num2: float = Form(...),

    # operation indicates add/subtract/multiply/divide
    operation: str = Form(...)
):

    try:
        # Call the calculate function imported earlier
        # This performs the requested math operation
        result = calculate(num1, num2, operation)

        # Return the result as JSON
        return {"result": result}

    except ValueError as e:
        # If something goes wrong (e.g., divide by zero)
        # return an error response with HTTP status code 400
        return JSONResponse(status_code=400, content={"error": str(e)})


# Define another API endpoint for AI explanation
# This endpoint accepts POST requests at /explain
@app.post("/explain")
def explain_api(

    # Get first number from form
    num1: float = Form(...),

    # Get second number from form
    num2: float = Form(...),

    # Get selected operation
    operation: str = Form(...)
):

    try:
        # First calculate the result using the calculator logic
        result = calculate(num1, num2, operation)

        # Build a prompt that will be sent to OpenAI
        # The AI will explain the calculation in simple language
        prompt = (
            f"Explain this calculation in very simple beginner-friendly language.\n"
            f"First number: {num1}\n"
            f"Second number: {num2}\n"
            f"Operation: {operation}\n"
            f"Result: {result}"
        )

        # Send the prompt to OpenAI's model
        # model="gpt-4.1-mini" is a lightweight model suitable for simple tasks
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        # Return both the result and the AI explanation
        return {
            "result": result,
            "explanation": response.output_text
        }

    except ValueError as e:
        # If the calculation fails (e.g., invalid operation)
        return JSONResponse(status_code=400, content={"error": str(e)})

    except Exception as e:
        # Catch any unexpected server or API errors
        # Return HTTP status 500 for internal server error
        return JSONResponse(status_code=500, content={"error": str(e)})