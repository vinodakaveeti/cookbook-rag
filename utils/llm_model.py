import logging
import httpx

from fastapi import HTTPException
from pydantic import BaseModel, Field

from constants import OLLAMA_URL, MODEL_NAME


logger = logging.getLogger(__name__)


class RecipeResponse(BaseModel):
    found: bool = Field(
        description="Whether the requested recipe exists in the context"
    )
    recipe_name: str = Field(
        description="Name of the requested recipe"
    )
    cuisine: str | None = Field(
        description="Cuisine or country, if explicitly provided"
    )
    preparation_time: str | None = Field(
        description="Preparation time, if explicitly provided"
    )
    refrigeration_time: str | None = Field(
        description="Refrigeration time, if explicitly provided"
    )
    ingredients: list[str] = Field(
        description="Ingredients and quantities found in the context"
    )
    instructions: list[str] = Field(
        description="Cooking instructions in the correct order"
    )



COOKBOOK_SYSTEM_PROMPT = """
You are a cookbook recipe formatter.

Your task is to extract the requested recipe from the supplied context
and present only the final answer.

STRICT RULES:
1. Never output your analysis, reasoning, or search process.
2. Never write phrases such as "Let me analyze", "Looking at the context",
   "I found", "Let me check", or "The user is asking".
3. Do not describe how you selected the recipe.
4. Do not repeat the recipe or conclusion.
5. Do not include unrelated recipes.
6. Do not invent ingredients, quantities, or instructions.
7. Ignore PDF extraction artifacts and control characters.
8. Extract ingredients and quantities from the instructions if a
   separate ingredient list is unavailable.
9. If a quantity is ambiguous or contradictory, preserve the source
   wording or explicitly mark it as unclear. Do not guess.
10. Return only readable Markdown using this format. If information is unavailable, omit that field.
11. If the requested recipe cannot be found in the context, respond: "I couldn't find this recipe in the provided cookbook context."

OUTPUT ONLY THE FINAL RECIPE. NO PREFACE. NO ANALYSIS.
""".strip()


async def call_llm(context, query, system_prompt:str=COOKBOOK_SYSTEM_PROMPT):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": system_prompt

            },
            {
                "role": "user",
                "content": (
                    f"Cookbook context:\n{context}\n\n"
                    f"Question: {query}\n\n"
                    "Provide the final answer in readable Markdown."
                )
            }
        ],
        "format":RecipeResponse.model_json_schema(),
        "keep_alive": "30m",
        "think": False,
        "stream": False,
        "options": {
            "num_predict": 700,
            "temperature": 0.1,
        }
    }
    try:
        logger.info(f"Sending request to Ollama at {OLLAMA_URL} and request payload is {payload}")
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Received response from Ollama: {result}...")
            if "message" in result:
                if "content" in result["message"]:
                    return result["message"]["content"]
            else:
                return "The message field is not present in the response from llm."
    except httpx.TimeoutException:
        logger.error("Ollama request timed out after 90 seconds")
        raise HTTPException(
            status_code=504,
            detail="The LLM request timed out. The model may be taking too long to respond or the service may be unavailable."
        )
    except httpx.ConnectError as e:
        logger.error(f"Failed to connect to Ollama service: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Unable to connect to the LLM service at {OLLAMA_URL}. Please ensure Ollama is running and accessible."
        )
    except httpx.HTTPError as e:
        logger.error(f"HTTP error from Ollama service: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Unable to communicate with the LLM service: {str(e)}"
        )
    except (ValueError, KeyError) as e:
        logger.error(f"Invalid response from Ollama: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail="The LLM returned an invalid response."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )