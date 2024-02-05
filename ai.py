import google.generativeai as palm  # Import the correct library
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
api_key = os.environ.get("GOOGLE_API_KEY")  # Use get() for safety


def search_ia_google(question):
    if api_key is None:
        raise ValueError("GOOGLE_API_KEY is not set in environment variables")

    try:
        palm.configure(api_key=api_key)

        models = [
            m
            for m in palm.list_models()
            if "generateText" in m.supported_generation_methods
        ]
        model = models[0].name

        prompt = """
        Your name is Riel, and you are an expert in agriculture. Please provide a clear and concise human answer, within 100 words, to any question related to agriculture. If the question is not related to agriculture, kindly request a rephrasing of the question.
        """
        prompt += question + "?"

        completion = palm.generate_text(
            model=model,
            prompt=prompt,
            temperature=0.5,
            max_output_tokens=100,
        )
        return completion.result

    except Exception as e:
        return "There was an error with the request. Please try again later."
