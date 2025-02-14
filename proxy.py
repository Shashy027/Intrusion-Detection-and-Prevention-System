import os
import time
import logging
import redis
import requests
import psutil
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
from threading import Thread
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

TARGET_SERVERS = ["http://127.0.0.1:8001"]
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
logging.basicConfig(filename="security_logs.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# **Rate Limiting Configurations**
MAX_REQUESTS_PER_SECOND = 10  # Block if IP sends more than 10 requests/sec
BLACKLIST_DURATION = 300  # Blacklist duration in seconds (5 minutes)


@app.route('/')
def dashboard():
    return render_template("dashboard.html")


@app.route('/api/logs')
def get_logs():
    logs = redis_client.lrange("request_logs", 0, 20)  # Fetch latest 20 logs
    return jsonify([eval(log) for log in logs])


@app.route('/proxy', methods=['POST'])
def proxy_request():
    ip = request.remote_addr
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    # **Check if the IP is already blacklisted**
    if redis_client.sismember("blocked_ips", ip):
        log_entry = {"ip": ip, "status": "blocked", "timestamp": timestamp}
        redis_client.lpush("request_logs", str(log_entry))
        redis_client.ltrim("request_logs", 0, 19)
        socketio.emit("update_data", get_dashboard_data())
        return jsonify({"error": "Your IP is blacklisted."}), 403

    # **Track requests per second**
    current_time = int(time.time())  # Get the current timestamp in seconds
    redis_key = f"request_rate:{ip}"

    # **Increment request count**
    redis_client.incr(redis_key)
    redis_client.expire(redis_key, 2)  # Expire after 2 seconds

    # **Check request count**
    request_count = int(redis_client.get(redis_key) or 0)

    if request_count > MAX_REQUESTS_PER_SECOND:
        redis_client.sadd("blocked_ips", ip)
        redis_client.expire("blocked_ips", BLACKLIST_DURATION)  # Remove after 5 min
        logging.info(f"IP {ip} automatically blacklisted for exceeding rate limit")

        socketio.emit("update_data", get_dashboard_data())

        return jsonify({"error": "Too many requests! Your IP has been blacklisted for 5 minutes."}), 429

    # **Forward request to backend**
    try:
        response = requests.post(f"{TARGET_SERVERS[0]}/proxy", json=request.get_json())
        response_data = response.json()

        log_entry = {"ip": ip, "status": "allowed", "timestamp": timestamp}
        redis_client.lpush("request_logs", str(log_entry))
        redis_client.ltrim("request_logs", 0, 19)

        # **Store request count per minute**
        current_minute = datetime.now().strftime("%Y-%m-%d %H:%M")
        redis_client.hincrby("request_history_per_minute", current_minute, 1)

        socketio.emit("update_data", get_dashboard_data())

        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": "Failed to connect to backend", "details": str(e)}), 500


@app.route('/api/blacklist', methods=['POST'])
def blacklist_ip():
    data = request.json
    ip = data.get('ip')
    if ip:
        redis_client.sadd("blocked_ips", ip)
        redis_client.expire("blocked_ips", BLACKLIST_DURATION)
        logging.info(f"IP {ip} manually added to blacklist")
        socketio.emit("update_data", get_dashboard_data())
        return jsonify({"message": f"IP {ip} blacklisted successfully!"})
    return jsonify({"error": "Invalid IP"}), 400


@app.route('/api/unblock/<ip>', methods=['POST'])
def unblock_ip(ip):
    if redis_client.srem("blocked_ips", ip):
        logging.info(f"IP {ip} removed from blacklist")
        socketio.emit("update_data", get_dashboard_data())
        return jsonify({"message": f"IP {ip} unblocked successfully!"})
    return jsonify({"error": "IP not found in blacklist"})


@app.route('/api/traffic-history')
def get_traffic_history():
    history = redis_client.hgetall("request_history_per_minute")
    return jsonify(history)


def get_dashboard_data():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "active_requests": len(redis_client.lrange("request_logs", 0, -1)),
        "request_logs": [eval(log) for log in redis_client.lrange("request_logs", 0, 20)],
        "blocked_ips": list(redis_client.smembers("blocked_ips")),
        "traffic_history": redis_client.hgetall("request_history_per_minute")
    }


def monitor_system():
    while True:
        time.sleep(1)
        socketio.emit("update_data", get_dashboard_data())


Thread(target=monitor_system, daemon=True).start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)