#!/usr/bin/env python3
"""
Phone Agent Web Service - AI-powered phone automation via web interface.
"""

import sys
import os
from flask import Flask, request, jsonify, render_template_string

# Import existing modules from the project
sys.path.append('.')
from phone_agent import PhoneAgent
from phone_agent.agent import AgentConfig
from phone_agent.model import ModelConfig
from main import check_system_requirements, check_model_api

# Initialize Flask app
app = Flask(__name__)

# Create global agent instance (will be initialized when first request is received)
agent = None

# Hardcoded configuration parameters
BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
MODEL_NAME = "autoglm-phone"
API_KEY = "2b55beee279d437ea8c7460e29bc12b0.X0JeFydsJjZjp4Rf"
MAX_STEPS = 100
DEVICE_ID = None
LANG = "zh"

# HTML template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Phone Agent Web Interface</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        form {
            display: flex;
            flex-direction: column;
        }
        label {
            font-weight: bold;
            margin-bottom: 10px;
            color: #555;
        }
        textarea {
            width: 100%;
            height: 100px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
            resize: vertical;
            margin-bottom: 20px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #45a049;
        }
        button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 20px;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Phone Agent 任务执行</h1>
        <form id="taskForm">
            <label for="task">请输入任务指令：</label>
            <textarea id="task" name="task" placeholder="例如：打开美团搜索附近的火锅店" required></textarea>
            <button type="submit" id="submitBtn">执行任务</button>
        </form>
        <div class="loading" id="loading" style="display: none;">
            <div class="spinner"></div>
            <span>正在执行任务，请稍候...</span>
        </div>
    </div>

    <script>
        document.getElementById('taskForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const task = document.getElementById('task').value;
            const submitBtn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            
            // Show loading state
            submitBtn.disabled = true;
            loading.style.display = 'flex';
            
            // Submit task to backend
            fetch('/api/run-task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ task: task }),
            })
            .then(() => {
                // Task submitted successfully, just hide loading
                submitBtn.disabled = false;
                loading.style.display = 'none';
            })
            .catch(() => {
                // If there's an error, just hide loading
                submitBtn.disabled = false;
                loading.style.display = 'none';
            });
        });
    </script>
</body>
</html>
'''

def initialize_agent():
    """
    Initialize the PhoneAgent instance if it doesn't exist yet.
    """
    global agent
    
    if agent is None:
        # Run system checks
        if not check_system_requirements():
            raise Exception("System requirements check failed")
        
        if not check_model_api(BASE_URL, MODEL_NAME, API_KEY):
            raise Exception("Model API check failed")
        
        # Create configurations using hardcoded parameters
        model_config = ModelConfig(
            base_url=BASE_URL,
            model_name=MODEL_NAME,
            api_key=API_KEY,
        )
        
        agent_config = AgentConfig(
            max_steps=MAX_STEPS,
            device_id=DEVICE_ID,
            verbose=True,  # Always show verbose output
            lang=LANG,
        )
        
        # Create agent instance
        agent = PhoneAgent(
            model_config=model_config,
            agent_config=agent_config,
        )

@app.route('/')
def index():
    """
    Render the main web interface.
    """
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/run-task', methods=['POST'])
def run_task():
    """
    API endpoint to run a phone agent task in background.
    
    Request JSON format:
    {
        "task": "任务指令内容"
    }
    
    Response JSON format:
    {
        "success": true/false,
        "message": "任务已提交到后台执行" / "错误信息"
    }
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data or 'task' not in data:
            return jsonify({"success": False, "message": "Missing task parameter"}), 400
        
        task = data['task'].strip()
        if not task:
            return jsonify({"success": False, "message": "Task cannot be empty"}), 400
        
        # Initialize agent if not already initialized
        initialize_agent()
        
        # Run the task in background - execute the full interaction flow until completion
        print(f"📋 Starting task execution in background: {task}")
        
        # Run the task asynchronously to avoid blocking the response
        def run_task_in_background():
            try:
                result = agent.run(task)
                print(f"✅ Task execution completed: {task}")
                print(f"   Final result: {result}")
            except Exception as e:
                print(f"❌ Task execution failed: {task}")
                print(f"   Error: {str(e)}")
        
        # Start the task in a separate thread
        import threading
        thread = threading.Thread(target=run_task_in_background)
        thread.daemon = True
        thread.start()
        
        # Return simple success response immediately
        return jsonify({"success": True, "message": "任务已提交到后台执行"})
        
    except Exception as e:
        # Return error response
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    # Get host and port from environment variables or use defaults
    host = os.getenv("PHONE_AGENT_WEB_HOST", "0.0.0.0")
    port = int(os.getenv("PHONE_AGENT_WEB_PORT", "5000"))
    
    print(f"🚀 Starting Phone Agent Web Service on http://{host}:{port}")
    print(f"📱 Web interface available at: http://{host}:{port}/")
    print(f"🔌 API endpoint: http://{host}:{port}/api/run-task")
    print(f"\nPress Ctrl+C to stop the server\n")
    
    # Run the Flask app
    app.run(host=host, port=port, debug=False)
