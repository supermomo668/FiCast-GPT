from pydantic import BaseModel

class Podcaster(BaseModel):
    name: str
    description: str
    mode: str = "podcast"

    def introduce(self):
        return f"{self.name} is {self.description}."
