# Intrusion-Detection-and-Prevention-System
This project focuses on securing educational institutions against DDoS attacks by implementing an Intrusion Prevention System (IPS) using a Flask-based reverse proxy. The system is designed to detect, analyze, and mitigate malicious traffic in real time while ensuring that legitimate users can access online resources without disruption.
Using Threat Intelligence APIs, Flask-SocketIO for real-time monitoring, and Redis for efficient caching, the system automatically blocks malicious IP addresses, enforces rate limiting, and provides a dashboard for administrators to monitor network activity. The primary goal is to minimize service downtime and protect institutional networks from cyber threats.

**Key Features:**

✅ Reverse Proxy-Based Security – Intercepts and filters all incoming traffic before reaching the backend server.

✅ Real-Time Threat Detection – Uses Threat Intelligence APIs (e.g., VirusTotal) to identify and block known malicious IPs.

✅ Rate Limiting Mechanism – Prevents excessive requests from overwhelming the server by automatically blocking high-volume traffic.

✅ Real-Time Monitoring Dashboard – Displays CPU usage, request count, memory consumption, request logs, and blocked IPs dynamically.

✅ Automatic & Manual IP Blacklisting – Identifies attackers in real time and allows administrators to block/unblock IPs as needed.

✅ Efficient Data Storage & Logging – Uses Redis to store blacklisted IPs and improve request processing speed.

✅ Simulated Attack Testing – Allows for testing under real-world attack conditions to analyze system performance and efficiency.



**Technologies Used:**

🔹 Programming Language: Python

🔹 Framework: Flask

🔹 Real-Time Monitoring: Flask-SocketIO

🔹 Database & Caching: Redis

🔹 Threat Intelligence: VirusTotal API (or similar APIs)

🔹 Visualization: Chart.js (for graphical representation of real-time data)

🔹 Deployment: Ubuntu VM



## Commands to run ##

**Clone the repo**

https://github.com/Shashy027/Intrusion-Detection-and-Prevention-System.git

**start redis**

redis-server

**start Backend**

python3 backend.py

**start proxy**

python3 proxy.py

# TIPS: #
redis-cli FLUSHALL // cleans the redis and refreshes

curl -X POST http://127.0.0.1:5000/proxy -H "Content-Type: application/json" -d '{"test": "data"}' // sending requests

for i in {1..15}; do curl -X POST http://127.0.0.1:5000/proxy -H "Content-Type: application/json" -d '{"test": "data"}'; done // performing a DDOS attack







