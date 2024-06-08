import praw
import requests
from bs4 import BeautifulSoup
import json
import os

# Initializing Reddit API
reddit = praw.Reddit(
    client_id="VlaZdnwb9BdcthBBB6hdRw",
    client_secret="TuEsRYMRxDKj2MdV0rrWDr4lLuIkDA",
    password="CS172Project",
    user_agent="CS172 Project",
    username="Slight_Ad3391",
)

def get_title_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.title.text.strip()
    except Exception as e:
        print("Error fetching title:", e)
        return None
    
# Function to process Reddit posts
def process_post(post):
    data = {
        "id": post.id,  # Include post ID
        "title": post.title,
        "author": post.author.name if post.author else "[deleted]",
        "url": post.url
    }
    if "reddit.com" not in post.url and post.url.endswith(".html"):
        data["html_title"] = get_title_from_url(post.url)
    return data

def crawl_reddit(subreddit_name, output_file, max_size=500):
    visited_ids = set()
    with open(output_file, 'a') as f:
        total_size = os.path.getsize(output_file)
        subreddit = reddit.subreddit(subreddit_name)
        for post in subreddit.new(limit=None):
            if post.id in visited_ids:
                continue
            post_data = process_post(post)
            json.dump(post_data, f)
            f.write('\n')
            visited_ids.add(post.id)
            # Update total size after each write
            total_size += len(json.dumps(post_data)) + 1  # +1 for newline character
            if total_size > max_size * 1024 * 1024:
                break

def remove_duplicates(input_file, output_file):
    seen_ids = set()
    unique_data = []

    with open(input_file, 'r') as f:
        for line in f:
            try:
                post_data = json.loads(line)
                if post_data["id"] not in seen_ids:
                    seen_ids.add(post_data["id"])
                    unique_data.append(post_data)
            except json.JSONDecodeError:
                print(f"Skipping line due to JSONDecodeError: {line}")
                continue
            except KeyError:
                print(f"Skipping line due to missing 'id': {line}")
                continue
    
    with open(output_file, 'w') as f:
        for data in unique_data:
            json.dump(data, f)
            f.write("\n")

# Main function
if __name__ == "__main__":
    subreddit_name = "ucr"
    output_file = "reddit_posts_ucr.json"
    try:
        crawl_reddit(subreddit_name, output_file)
        remove_duplicates(output_file, "reddit_posts_ucr_unique.json")
        print("Crawling completed successfully.")
    except Exception as e:
        print("Error:", e)
