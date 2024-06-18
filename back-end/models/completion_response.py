from pydantic import Field,BaseModel

class CompletionResponse(BaseModel):
    message: str = Field(
        title="The generated response from GPT.",
        example="AI Hub is AI based application",
    )
    prompt_tokens: int = Field(
        title="Total token used in prompt.", example=100
    )
    completion_tokens: int = Field(
        title="Total token used in completion.", example=100
    )
    total_cost: float = Field(
        title="Total cost in USD ($) for the request.", example=0.01, default=None
    )
