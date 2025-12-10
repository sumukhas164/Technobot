# TechnoBot – AI-Powered Technical Assistant (MCP + Groq + Flask)

TechnoBot is an advanced AI-driven technical assistant built using **Flask**, **Groq LLM**, and **FastMCP tools**.  
It handles technical troubleshooting, performs multi-source research, and raises/reads tickets using a MySQL backend.  
The system produces **clean, structured, step-by-step** LLM responses.

---

## ✨ Key Features

- 🔍 **Technical Query Solver**  
  Automatically uses MCP research tools (DuckDuckGo, Wikipedia, Research API) to answer queries.

- 🛠️ **Troubleshooting Steps**  
  Delivers clear, step-by-step technical resolutions and command instructions.

- 🎫 **Smart Ticketing System**  
  Uses MySQL-based ticket tool **only when the query contains** “ticket” or “raise ticket”.

- ⚡ **Fast Response Engine**  
  Groq LLM + FastMCP tools = fast, accurate, structured responses.

- 🎨 **Responsive Frontend**  
  Flask + HTML/CSS/JS interface with incremental LLM output streaming.

---

## 🏗️ Architecture

The project contains the following components:

### **1. Flask Client (`client.py` / `app.py`)**
- Takes user queries  
- Sends queries to MCP Server using **SSE (Server-Sent Events)**  
- Displays streaming output from LLM  
- Renders step-by-step structured responses

### **2. MCP Server (`server.py`)**
- Hosts all available MCP tools:
  - Wikipedia
  - DuckDuckGo search
  - Research tool
  - Ticket database tool
- Sends tool schema to Groq LLLM

### **3. Groq LLM (Client-Side MCP Integration)**
- Uses all MCP tools **except ticket tool by default**
- Ticket tool is used **only if the query contains**:
  - “ticket”
  - “raise ticket”

---

## 📌 Architecture Flow Diagram  
![Architecture Diagram](path/to/architecture.jpg)

---

## 🎬 Demo Video  
[Demo Video Link Here]

---

## 📸 Sample Output Screenshots  

![Sample Output 1](path/to/screenshot1.png)  
![Sample Output 2](path/to/screenshot2.png)  
![Sample Output 3](path/to/screenshot3.png)

---

# ⚙️ Installation

## 1️⃣ Clone the Project
```bash
git clone https://github.com/your-username/technobot.git
cd technobot
```

## 2️⃣ Create Virtual Environment
```bash
python -m venv venv
```

### Activate:
Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

## 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

---

# 🔧 Environment Setup (.env)

```ini
GROQ_API_KEY=your_groq_key
FLASK_SECRET_KEY=your_flask_secret
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=technical_db
```

---

# ▶️ Running the System

## Run MCP Server
```bash
python server.py
```

## Run Flask Client
```bash
python client.py
```

Open browser:
```
http://127.0.0.1:5000
```

---

# 🕹️ Usage Workflow

## ✔️ Technical Problem Query
Example:
```
docker image not running
```

## ✔️ Ticket Query
Example:
```
raise ticket for email issue
check ticket 102
```

---

# 🧩 Technology Stack

| Component   | Technology |
|------------|------------|
| LLM        | Groq API |
| Tools      | FastMCP |
| Backend    | Flask |
| Database   | MySQL |
| Search     | DDGS |
| Frontend   | HTML, CSS, JS |
| Protocol   | SSE |

---

# 📄 License
MIT License © 2025

---

# ❤️ Credits
Built by **Sumukha**
