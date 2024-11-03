import requests
import csv
import os

GITHUB_TOKEN = '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'

# Define the headers for the requests
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


def get_boston_users():
    users = []
    page = 1
    while True:
        response = requests.get(
            f"https://api.github.com/search/users",
            params={
                "q": "location:Boston followers:>100",
                "per_page": 100,
                "page": page
            },
            headers={"Authorization": f"Bearer {GITHUB_TOKEN}"}
        )
        data = response.json()
        if "items" in data:
            users.extend(data["items"])
            # If less than 100 items returned, we've reached the last page
            if len(data["items"]) < 100:
                break
            page += 1
        else:
            break
    return users

def get_user_details(login):
    response = requests.get(f"https://api.github.com/users/{login}",
                            headers={"Authorization": f"Bearer {GITHUB_TOKEN}"})
    return response.json()

def save_users_to_csv(users):
    with open('users.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            "login", "name", "company", "location", "email",
            "hireable", "bio", "public_repos", "followers",
            "following", "created_at"
        ])
        writer.writeheader()

        for user in users:
            user_details = get_user_details(user['login'])  # Fetch user details
            
            if user_details:
                # Handle the company field safely
                company = user_details.get("company")
                if company is None:
                    company = ""  # Default to empty string if None
                else:
                    company = company.replace("@", "").strip().upper()  # Clean up
                
                writer.writerow({
                    "login": user['login'],
                    "name": user_details.get("name", ""),
                    "company": company,
                    "location": user_details.get("location", ""),
                    "email": user_details.get("email", ""),
                    "hireable": user_details.get("hireable", False),  # Defaulting to False
                    "bio": user_details.get("bio", ""),
                    "public_repos": user_details.get("public_repos", 0),
                    "followers": user_details.get("followers", 0),
                    "following": user_details.get("following", 0),
                    "created_at": user_details.get("created_at", ""),
                })
            else:
                print(f"Failed to fetch details for user: {user['login']}")



def save_repos_to_csv(users):
    repos_data = []
    for user in users:
        username = user['login']
        repos_url = f"https://api.github.com/users/{username}/repos?per_page=500"
        repos_response = requests.get(repos_url, headers=headers)

        # Check if the response was successful
        if repos_response.status_code == 200:
            repositories = repos_response.json()

            for repo in repositories:
                # Check if repo is a dictionary and not None
                if isinstance(repo, dict):
                    license_name = ""
                    if "license" in repo and repo["license"] is not None:
                        license_name = repo["license"].get("key", "")
                    
                    repos_data.append({
                        "login": username,
                        "full_name": repo.get("full_name", ""),
                        "created_at": repo.get("created_at", ""),
                        "stargazers_count": repo.get("stargazers_count", 0),
                        "watchers_count": repo.get("watchers_count", 0),
                        "language": repo.get("language", ""),
                        "has_projects": repo.get("has_projects", False),
                        "has_wiki": repo.get("has_wiki", False),
                        "license_name": license_name
                    })
                else:
                    print(f"Warning: Expected a dictionary for repo but got {repo}")  # Debugging output

        else:
            print(f"Error fetching repositories for {username}: {repos_response.status_code}")  # Debugging output

    # Save the repositories data to CSV
    with open('repositories.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            "login", "full_name", "created_at", "stargazers_count", 
            "watchers_count", "language", "has_projects", 
            "has_wiki", "license_name"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(repos_data)

if __name__ == "__main__":
    users = get_boston_users()
    save_users_to_csv(users)
    save_repos_to_csv(users)