import re

with open('app/integrations/sorare/websocket.py', 'r') as f:
    content = f.read()

replacement = """headers = {}
                if self.api_key:
                    headers["APIKEY"] = self.api_key
                if self.jwt_token:
                    headers["Authorization"] = f"Bearer {self.jwt_token}"
                    headers["JWT-AUD"] = "scoutlab" """

content = re.sub(r'headers = \{\}\s*if self\.api_key:\s*headers\["APIKEY"\] = self\.api_key', replacement, content)

with open('app/integrations/sorare/websocket.py', 'w') as f:
    f.write(content)

