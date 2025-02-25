import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_CRED = os.getenv('MONGO_CRED')

app = Flask(__name__)
client = MongoClient(MONGO_CRED)
db = client["esp32_dht11"]
collection = db["readings"]


@app.route("/dht11/store", methods=["POST"])
def store_dht11():
    raw = request.json
    if "temperature" in raw and "humidity" in raw:
        data = {
            "device_id": "dht11",
            "temperature": raw["temperature"],
            "humidity": raw["humidity"]
        }
        collection.insert_one(data)
        return jsonify({"message": "Data stored successfully"}), 201
    return jsonify({"error": "Invalid data format"}), 400


@app.route("/pir/store", methods=["POST"])
def store_pir():
    raw = request.json
    if "motion_detected" in raw:
        data = {
            "device_id": "pir",
            "motion_detected": raw["motion_detected"],
        }
        collection.insert_one(data)
        return jsonify({"message": "Data stored successfully"}), 201
    return jsonify({"error": "Invalid data format"}), 400


if __name__ == "__main__":
    app.run(debug=True)
