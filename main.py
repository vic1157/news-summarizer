import openai
from dotenv import find_dotenv, load_dotenv
import os 
import requests
import json
import time 

load_dotenv()
news_api_key = os.environ.get("NEWS_API_KEY")


client = openai.OpenAI()

#This is an older model
model = "gpt-3.5-turbo-16k"

#TBD
def main():
	news = get_news("bitcoin")
	#print(bitcoin_news[0])
	
	
#Foundation of Application; will get news from the news API
def get_news(topic):
	url = (
		f"https://newsapi.org/v2/everything?q={topic}&apiKey={news_api_key}"
	)
	
	try:
		response =  requests.get(url)
		if response.status_code == 200:
			news = json.dumps(response.json(), indent=4)
			print(news)
			news_json = json.loads(news)
			#print(news_json)
			
			data = news_json
			
			#Access all the fields == loop through all the items within the JSON
			status = data["status"]
			total_results = data["totalResults"]
			articles = data["articles"]
			final_news = []
			
			#Loop through articles
			for article in articles:
				source_name = article["source"]["name"]
				author = article["author"]
				title = article["title"]
				description = article["description"]
				url = article["url"]
				content = article["content"]
				title_description = f"""
				Title: {title}, 
				Author: {author}, 
				Source: {source_name}, 
				Description: {description}, 
				URL: {url}
				"""
				final_news.append(title_description)
			return final_news
		else:
			return []
		
	except requests.exceptions.RequestException as e:
		print("Error occurred during API Request", e)


if __name__ == "__main__":
	main()
