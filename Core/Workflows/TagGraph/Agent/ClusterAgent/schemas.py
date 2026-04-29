from pydantic import BaseModel, Field


class cluster(BaseModel):
    cluster_title: str = Field(description="1-3 word title of that key phrase")
    members: list[int] = Field(
        description="list of all the titles that represent this cluster"
    )


class clusterOutput(BaseModel):
    clusters: list[cluster] = Field(
        description="list of all the key themes focused in the review"
    )
    rejected_titles: list[int] = Field(
        description="list of all the titles that does not focus on product's feature"
    )
