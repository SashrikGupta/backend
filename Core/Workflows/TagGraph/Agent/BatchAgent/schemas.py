from pydantic import BaseModel, Field


class KeyPrhase(BaseModel):
    title: str = Field(description="1-3 word title of that key phrase")
    keyphrase: str = Field(
        description="The key phrase exactly cut from the review min lenght should be 3 and max lenght should be 7-8 words"
    )
    sentiment: int = Field(
        description="sentiment core from 0 to 10 0 beign negative 10 being pposetive"
    )


class ReviewData(BaseModel):
    id: int = Field(description="review id , exactly the review id of the review")
    review_data: list[KeyPrhase] = Field(
        description="list of all the key phraess foucn in the review "
    )


class BatchReviewOutput(BaseModel):
    reviews: list[ReviewData] = Field(
        description="list of all the key phraess foucn in the review "
    )
