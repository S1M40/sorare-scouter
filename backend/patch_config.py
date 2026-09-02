import re

with open('app/config.py', 'r') as f:
    content = f.read()

replacement = """    DEBUG: bool = True

    @field_validator("DEBUG", "DEMO_MODE", mode="before")
    @classmethod
    def parse_bool(cls, v) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            v_lower = v.lower()
            if v_lower in ("false", "0", "no", "f", "release"):
                return False
            return True
        return bool(v)"""

content = re.sub(r'    DEBUG: bool = True', replacement, content)

with open('app/config.py', 'w') as f:
    f.write(content)

