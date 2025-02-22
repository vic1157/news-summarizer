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
			return ''.join(final_news)
		else:
			return []
		
	except requests.exceptions.RequestException as e:
		print("Error occurred during API Request", e)


class AssistantManager:
	thread_id = None
	assistant_id = None

	def __init__(self, model: str = model):
		self.client = client,
		self.model = model,
		self.assistant = None,
		self.thread = None,
		self.run = None,
		self.summary = None
	
	def retrieve_assistant(self):
		if AssistantManager.assistant_id:
			self.assistant = self.client.beta.assistants.retrieve(
			assistant_id = AssistantManager.assistant_idd
		)

	def retrieve_thread(self):
		if AssistantManager.thread_id:
			self.thread = self.client.beta.threads.retrieve(
				thread_id = AssistantManager.thread_id
			)
	
	# Creates an assistant object if it doesn't exist
	def create_assistant(self, name, instructions, tools):
		if not self.assistant:
			assistant_obj = self.client.beta.assistants.create(
				name=name,
				instructions=instructions,
				tools=tools,
				model=self.model
			)
			AssistantManager.assistant_id = assistant_obj.id
			self.assistant = assistant_obj
			print(f'AssistID:::: {self.assistant.id}')
	
	# Creates a thread object if it doesn't exist
	def create_thread(self):
		if not self.thread:
			thread_obj = self.client.beta.threads.create()
			AssistantManager.thread_id = thread_obj.id
			self.thread = thread_obj
			print(f'ThreadID::: {self.thread.id}')
	
	# Adds a message to an existing thread
	def add_message_to_thread(self, role, content):
		if self.thread:
			self.client.beta.threads.messages.create(
				thread_id = self.thread.id,
				role=role,
				content=content
			)
	
	# Checks if a thread and an assistant object exists before execting run
	def run_assistant(self, instructions):
		if self.thread and self.assistant:
			self.run = self.client.beta.threads.runs.create(
				thread_id=self.thread.id,
				assistant_id=self.assistant.id,
				instructions=instructions
			)
	
	# Retrieves the response from the model
	def process_message(self):
		if self.thread:
			messages = self.client.beta.threads.messages.list(self.thread_id)
			summary = []
			
			last_message = messages.data[0]
			role = last_message.role
			response = last_message.role.content[0].text.value
			summary.append(response)
			
			print(f"SUMMARY ---> {role.capitalize()}: ==> {response}")
		self.summary = '\n'.join(summary)

if __name__ == "__main__":
	main()
