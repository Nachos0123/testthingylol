from dataclasses import dataclass

@dataclass
class Example:

    example:str      = ""

    def to_dict(self):
        return {
            "accessToken"      : self.example
        }
    
    @classmethod
    def from_dict(cls, data:dict):
        return cls(
            data.get("example", "")
        )