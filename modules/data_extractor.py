from openai import OpenAI
from dotenv import dotenv_values
import json
import pandas as pd

class DataExtractor:
    def __init__(self, entry, date, source_name, prompt):
        self.entry = entry
        self.date = date
        self.source_name = source_name
        self.prompt = prompt
        self.config = dotenv_values('.env')
        self.client = OpenAI(api_key=self.config.get('OPENAI_API_KEY'))

    def extract(self):
        print(f"Extracting data for {self.source_name} with ChatGPT...")
        entry = self.entry
        prompt = self.prompt

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt + "\n\n" + entry
                        }
                    ]
                }
            ],
            temperature=1,
            max_tokens=5000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={
                "type": "json_object"
            }
        )

        response_text = response.choices[0].message.content
        print("Data extracted successfully!\n")

        return response_text

    def text_to_df(self, text):
        print("Converting extracted data to DataFrames...")
        data = json.loads(text)
        data_df = {}
        for key in data:
            data_df[key] = pd.DataFrame(data[key])
            if len(data_df[key]) == 0:
                continue
            data_df[key]['Source'] = self.source_name
            data_df[key]['Published'] = self.date

        print("Data converted to DataFrames successfully!\n")
        return data_df
