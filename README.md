# Babu-Lohar: A Slack Bot Powered by Advanced LLM Model for Interacting with Uploaded PDFs

## Introduction
Babu-Lohar is a versatile Slack Bot that is powered by an advanced Large Language Model (LLM). It is designed to interact with your uploaded Documents, extract useful information, and assist in analyzing and managing content.

## Features
- Documents Uploading: Upload your Documents files to the Slack channel and Babu-Lohar will automatically process them.
- Chat with your documents.
- Documents summarization.
- Advanced Language Understanding: Powered by the latest language understanding model, Babu-Lohar can understand and execute complex commands, and even engage in casual conversation.

## Installation

1. **Clone the Repository**

   First, clone the Babu-Lohar repository from GitHub to your local machine. Use the following command:

   ```
   git clone https://github.com/Madhav-MKNC/Babu-LOHAR.git;
   cd Babu-LOHAR/;
   ```

2. **Setup Environment**

   Install the required dependencies for Babu-Lohar. It is recommended to use a virtual environment to keep your project organized.

   ```
   pip install -r requirements.txt
   ```

3. **Configure Your Slack Workspace**

   Create a new bot in your Slack workspace and obtain your `Bot User OAuth Token`.

4. **Set Up Environment Variables**

   You will need to set up all the environment variables mentioned in the .env file. (Make sure that this part remains as secure as possible)

5. **Run the Bot**

   Once you have everything set up, you can run Babu-Lohar using the following command:

   ```
   python main.py
   ```

## Usage
Once Babu-Lohar is up and running, you can begin uploading PDFs to your Slack workspace. The bot will automatically process any PDFs uploaded to channels it is a member of.

To interact with Babu-Lohar, simply mention the bot in a message.

## License
Babu-Lohar is licensed under the [MIT License](LICENSE.md). 

## Acknowledgements
We are grateful to OpenAI for their incredible GPT models which power Babu-Lohar. Additionally, we would like to express our thanks to hwchase17 for the Langchain framework, which has greatly contributed to the development of our project.

## Contact
For any questions or concerns, please open an issue on GitHub or contact the maintainers directly.

Enjoy using Babu-Lohar!
