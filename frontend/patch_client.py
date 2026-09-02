import re

with open('src/services/api/client.ts', 'r') as f:
    content = f.read()

replacement = """export const API_BASE_URL = import.meta.env["VITE_API_BASE_URL"] ?? "";

export const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API === "true" || (!API_BASE_URL && import.meta.env.DEV);"""

content = re.sub(r'export const API_BASE_URL = .*?\n\nexport const USE_MOCK_API = !API_BASE_URL;', replacement, content, flags=re.DOTALL)

with open('src/services/api/client.ts', 'w') as f:
    f.write(content)

