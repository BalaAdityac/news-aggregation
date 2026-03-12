How to Run the n8n Workflow
1. Install Docker
Install Docker Desktop if it is not installed.

Download:
https://www.docker.com/products/docker-desktop

Start Docker Desktop and wait until it says it is running.

2. Run n8n using Docker
Run this command in terminal:

docker run -it --rm -p 5678:5678 n8nio/n8n
This starts n8n locally.

Then open in browser:

http://localhost:5678
3. Download the Workflow from the Repository
Clone the repository:

git clone https://github.com/BalaAdityac/news-aggregation.git
Go to the workflow folder:

news-aggregation/n8n-workflow
You will find:

news-workflow.json
4. Import the Workflow into n8n
Inside the n8n editor:

Click Workflows

Click Import

Select Import from File

Choose:

news-workflow.json
The workflow will load into the editor.

5. Run the Workflow
Click:

Execute Workflow
The workflow will run and generate the newsletter output.

