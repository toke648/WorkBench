# AI Command Hub

**English** | [**简体中文**](README.md)

**AutoExecAI** is an AI-based intelligent tool that analyzes user needs and automatically generates terminal commands, executes commands to obtain results, and continues to execute the next command as needed. It understands user needs through natural language processing (NLP) and converts them into executable commands. Before each command is executed, the generated command will be displayed for the user to confirm whether to execute. Supports multiple rounds of dialogue until the task is completed.

## Features

- **Intelligent command generation**: Through natural language processing, analyze and generate corresponding terminal commands according to user needs.
- **Automatic command execution**: Automatically execute commands and return execution results without manual input by users.
- **Command confirmation**: Before each command is executed, the generated command is displayed and the user is asked to confirm whether to execute.
- **Multi-round dialogue**: Supports continuous dialogue until the task is completed. Users can enter new requirements at any time, and the system will continue to generate and execute commands according to the requirements.
- **Error handling and retry**: If the command execution fails, the system will automatically retry and feedback the error after several failures.

## Installation

### 1. Clone the project

```bash
git clone https://github.com/toke648/AutoExecAI.git
cd AutoExecAI
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up an API key

Before using this project, you need to obtain a valid OpenAI API key and configure it in the code. Please visit [OpenAI](https://platform.openai.com/account/api-keys) to obtain your API key.

Add the key to the `client = OpenAI(api_key="YOUR_API_KEY")` position in the `ai_thinker.py` file and replace it with your key.

## Usage

### Start the program

Run the following command in the terminal:

```bash
python main.py
```

Or run
```bash
python auto_ai.py
```

### Interactive use

The program will prompt you to enter the requirements. You can describe the tasks you need to perform. The system will analyze your request and display the generated commands:

```
Describe what you need to do (or type 'exit' to quit): I want to create a file called test.txt on Windows
Thinking... Please wait while I analyze your request.
Suggested command: echo. > test.txt
Do you want to execute this command? (yes/no):
```

- If you confirm to execute the command, the system will execute it in the background and return the result.
- If the command is executed successfully, you can continue to enter the next requirement, and the system will generate and execute the command according to the new requirement.
- If the execution fails, the system will automatically retry until the maximum number of retries is reached.

### Example

1. User inputs the requirement: "Create a test.txt file".

2. The system generates a command and asks for confirmation: "echo. > test.txt".

3. After the user confirms the execution, the system executes the command and displays the result.

4. If the execution is successful, continue to wait for the next dialogue.

## Development

### 1. Modify the requirement analysis and command generation

If you need to customize the requirement analysis and command generation logic, you can modify the `thinking_step` function in the `ai_thinker.py` file, which is responsible for converting user input into commands.

### 2. Improve the command execution process

If you need to add other command execution methods or error handling mechanisms, you can modify the `execute_command` function in `main.py`.

## Contribution

Welcome to raise questions or contribute code! Please submit questions or request features in the following ways:

- Fork this repository and submit a PR.

- Report bugs or make new feature requests in Issues.

## License

Apache License. See LICENSE for more information.