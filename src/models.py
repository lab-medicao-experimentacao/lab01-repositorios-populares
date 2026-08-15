from pydantic import BaseModel


class RepositoryRecord(BaseModel):
    nameWithOwner: str
    stargazerCount: int
    createdAt: str
    ageInDays: int
    mergedPullRequests: int
    totalReleases: int
    timeSinceLastUpdate: int
    primaryLanguage: str | None
    totalIssues: int
    closedIssues: int
    closedIssuesRatio: float | None
