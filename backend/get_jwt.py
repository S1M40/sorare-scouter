import os
import json
import urllib.request
import getpass
import re
import bcrypt

def get_jwt():
    print("=== Sorare JWT Generator (Bcrypt) ===")
    email = input("Sorare Email: ").strip()
    password = getpass.getpass("Sorare Password: ").strip()
    otp = input("Sorare 2FA Code (leave blank if you don't use 2FA): ").strip()

    # Step 1: Fetch the salt for this specific email
    print("\n1. Fetching your account's security salt from Sorare...")
    salt_url = f"https://api.sorare.com/api/v1/users/{urllib.parse.quote(email)}"
    try:
        req = urllib.request.Request(salt_url, headers={"User-Agent": "ScoutLab-Backend/1.0"})
        response = urllib.request.urlopen(req)
        user_data = json.loads(response.read())
        salt = user_data.get("salt")
        if not salt:
            print("❌ Could not find salt in the response. Is the email correct?")
            return
    except Exception as e:
        print(f"❌ Failed to fetch salt: {e}")
        return

    # Step 2: Hash the password using the retrieved salt
    print("2. Hashing password locally...")
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8')).decode('utf-8')

    # Step 3: Send the GraphQL Mutation
    print("3. Authenticating with Sorare...")
    graphql_url = "https://api.sorare.com/graphql"
    
    query = """
    mutation SignInMutation($input: signInInput!) {
      signIn(input: $input) {
        currentUser {
          slug
        }
        jwtToken(aud: "scoutlab") {
          token
        }
        errors {
          message
        }
      }
    }
    """
    
    variables = {
        "input": {
            "email": email,
            "password": hashed_password
        }
    }
    if otp:
        variables["input"]["otp"] = otp

    req = urllib.request.Request(graphql_url, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "ScoutLab-Backend/1.0")
    
    data = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    
    try:
        response = urllib.request.urlopen(req, data=data)
        result = json.loads(response.read())
        
        sign_in_data = result.get("data", {}).get("signIn", {})
        
        if not sign_in_data:
            print("❌ Unexpected API Response:", result)
            return

        errors = sign_in_data.get("errors", [])
        if errors:
            print(f"❌ Authentication Failed: {errors[0]['message']}")
            return
            
        token = sign_in_data.get("jwtToken", {}).get("token")
        if token:
            print("✅ Successfully retrieved JWT!")
            
            env_path = ".env"
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    content = f.read()
                
                content = re.sub(r'SORARE_JWT=.*', f'SORARE_JWT={token}', content)
                content = re.sub(r'DEMO_MODE=true', 'DEMO_MODE=false', content)
                
                with open(env_path, "w") as f:
                    f.write(content)
                print(f"✅ Automatically saved your JWT to .env and disabled DEMO_MODE!")
            else:
                print(f"Here is your JWT:\n{token}")
        else:
            print("❌ Failed to find token in response:", result)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    get_jwt()
