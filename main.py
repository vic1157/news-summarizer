import openai
from dotenv import find_dotenv, load_dotenv
import os 
import requests
import json
import time 
import streamlit as st

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
	
	# Executes function calling if required by a run
	def call_required_functions(self, required_action):
		if not self.run:
			return
		
		tool_outputs = []
		for action in required_action["tool_calls"]:
			func_name = action["function"]["name"]
			arguments = json.loads(action["function"]["arguments"])

			if func_name == "get_news":
				output = get_news(topic=arguments["topic"])
				print(f'Output of get_news(): {output}')
				tool_outputs.append({
					"tool_call_id": action["id"],
					"ouput": output
				})
			else:
				raise ValueError(f"Unknown function: {func_name}")
			print("Submitting outputs back to the Assistant...!")

		# Submit all tool ouputs at once after collecting them in a list
		if tool_outputs:
			try:
				self.run = client.beta.threads.runs.submit(
					thread_id = self.thread.id,
					run = self.run.id,
					tool_outputs = tool_outputs
				)
				print("Tool outputs submitted successfully.")
			except Exception as e:
				print("Failed to submit tool ouputs:", e)
		self.wait_for_completed()

	# for streamlit
	def get_summary(self):
		return self.summary

	# Waits for run to complete to confirm action or enter function calling
	def wait_for_completed(self):
		if self.thread and self.run:
			while True:
				time.sleep(5)
				run_status = self.client.beta.threads.runs.retrieve(
					thread_id= self.thread.id,
					run_id = self.run.id
				)
				print(f'RUN STATUS::: {run_status.model_dump_json(indent=4)}')
				
				# Processes the message if the run has been completed
				if run_status.status == 'completed':
					self.process_message()
					break
				elif run_status.status == "requires_action":
					print("FUNCTION CALLING NOW...")
					self.call_required_functions(
						run_status.required_action.submit_tool_outputs.model_dump()
					)

	# List run steps
	def run_steps(self):
		run_steps = self.client.beta.threads.runs.steps.list(
			thread_id=self.thread.id,
			run_id=self.run.id
		)
		print(f"Run-Steps::: {run_steps}")



if __name__ == "__main__":
	main()
