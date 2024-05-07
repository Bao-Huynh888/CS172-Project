import praw
import requests
from bs4 import BeautifulSoup
import json
import os

#Initializing Reddit API
reddit = praw.Reddit(
    client_id="VlaZdnwb9BdcthBBB6hdRw",
    client_secret="TuEsRYMRxDKj2MdV0rrWDr4lLuIkDA",
    password="CS172Project",
    user_agent=True,
    username="Slight_Ad3391",
)

def get_title_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.paser')
        return soup.title.text.strip()
    except Exception as e:
        print("Error fetching title:", e)
        return None
    
#Function to process Reddit posts
def process_post(post):
    data = {
        "title": post.title,
        "author": post.author.name if post.author else "[deleted]",
        "url": post.url
    }
    if "reddit.com" not in post.url and post.url.endswith(".html"):
        data["html_title"] = get_title_from_url(post.url)
    return data

def crawl_reddit(subreddit_name, output_file, max_size = 500):
    visited_Ids = set()
    with open(output_file, 'a') as f:
        total_size = os.path.getsize(output_file)
        subreddit = reddit.subreddit(subreddit_name)
        for post in subreddit.new(limit=None):
            if post.id in visited_Ids:
                continue
            post_data = process_post(post)
            json.dump(post_data, f)
            f.write('\n')
            visited_Ids.add(post.id)
            #checking file size
            total_size = os.path.getsize(output_file)
            if total_size > max_size * 1024 * 1024:
                break

#Main function
if __name__ == "__main__":
    subreddit_name = "ucr"
    output_file = "reddit_posts_ucr.json"
    try:
        crawl_reddit(subreddit_name, output_file)
        print("Crawling completed successfully.")
    except Exception as e:
        print("Error:", e)