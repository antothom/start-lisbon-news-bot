# START Lisbon Newsletter Automation

Welcome to the START Lisbon Newsletter Automation repository. This project is designed to automate the process of aggregating, categorizing, and generating newsletters for the START Lisbon community. By leveraging web scraping, machine learning, and the OpenAI API, this project aims to streamline the creation of high-quality, relevant newsletters.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- **News Aggregation**: Automatically fetches content from various newsletter sources.
- **Content Categorization**: Uses AI to categorize and prioritize news items.
- **Automated Drafting**: Generates draft newsletters based on aggregated content.
- **News Feed**: Publishes the most relevant news to a Slack channel for immediate consumption.

## Requirements

- Python 3.7+
- Virtual environment (optional but recommended)
- OpenAI API Key
- Slack API Token
- Libraries: `requests`, `beautifulsoup4`, `pandas`, `sqlalchemy`, `openai`

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/start-lisbon-newsletter.git
    cd start-lisbon-newsletter
    ```

2. **Set up a virtual environment:**

    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. **Set up environment variables:**

    Create a `.env` file in the root directory of the project and add the following environment variables:

    ```bash
    OPENAI_API_KEY=your_openai_api_key
    SLACK_API_TOKEN=your_slack_api_token
    SLACK_CHANNEL_ID=your_slack_channel_id
    DATABASE_URL=sqlite:///newsletters.db  # or any other database URL
    ```

2. **Update the configuration file:**

    Edit `config.py` to match your specific needs, such as the list of newsletter URLs to fetch.

## Usage

1. **Fetch newsletters:**

    Run the script to fetch and store newsletter content in the database.

    ```bash
    python fetch_newsletters.py
    ```

2. **Categorize and process news items:**

    Run the script to categorize and prioritize news items.

    ```bash
    python process_news.py
    ```

3. **Generate a draft newsletter:**

    Run the script to generate a draft newsletter.

    ```bash
    python draft_newsletter.py
    ```

4. **Publish news feed to Slack:**

    Run the script to publish the most relevant news to a Slack channel.

    ```bash
    python publish_to_slack.py
    ```

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
