from openai import OpenAI
from dotenv import load_dotenv

class DataExtractor:
    def __init__(self, entry, source_name, prompt):
        self.entry = entry
        self.source_name = source_name
        self.prompt = prompt
        self.client = OpenAI(api_key='')

    def extract(self):
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
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={
                "type": "json_object"
            }
        )

        response_text = response.choices[0].message.content

        return response_text
