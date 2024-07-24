from flask import Flask, jsonify, request
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.json_util import dumps, ObjectId
from datetime import datetime, timedelta
import random

app = Flask(__name__)

uri = "mongodb+srv://teguhrahmat911:edx4JgGgXvVvKdTb@kualitasudara.czsbrts.mongodb.net/?retryWrites=true&w=majority&appName=kualitasudara"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['kualitasudara1']  # ganti sesuai dengan nama database kalian
my_collection = db['kualitasudara2']  # ganti sesuai dengan nama collections kalian

def create_data_dump():
    # Hapus data lama jika ada
    my_collection.delete_many({})
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    # Tambahkan data dump (contoh data)
    for _ in range(1000):  # 1000 baris data contoh
        temperature = random.uniform(15, 40)
        humidity = random.uniform(40, 60)
        pm25 = random.uniform(10.0,40.0)
        # mq135 = round(random.uniform(0, 1000), 2)
        no2 = round(random.uniform(20.0, 55.0), 2)
        co = round(random.uniform(0.0, 1.0), 2)
        nh3 = round(random.uniform(5.5, 11.0), 2)
        
        #timestamp = datetime.now() - timedelta(minutes=random.randint(0, 1440))  # Data dari 24 jam terakhir
        #random_timestamp = start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())))
        delta = end_date - start_date
        delta_in_second = (delta.days * 24 * 60 * 60) + delta.seconds
        random_second = random.randrange(delta_in_second)
        random_timestamp =  start_date + timedelta(seconds=random_second)
        
        my_collection.insert_one({
            'temperature': temperature,
            'humidity': humidity,
            'pm25': pm25,
            # 'mq135': mq135,
            'no2': no2,
            'co': co,
            'nh3': nh3,
            'timestamp': random_timestamp
        })

@app.route('/latest_data', methods=['GET'])
def get_latest_data():
    latest_data = my_collection.find_one(sort=[('timestamp', -1)])
    latest_data['_id'] = str(latest_data['_id'])
    return jsonify(latest_data)

@app.route('/data', methods=['GET'])
def get_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = {}
    
    if start_date:
        query['timestamp'] = {'$gte': datetime.fromisoformat(start_date)}
    if end_date:
        if 'timestamp' in query:
            query['timestamp']['$lte'] = datetime.fromisoformat(end_date)
        else:
            query['timestamp'] = {'$lte': datetime.fromisoformat(end_date)}
    
    data = list(my_collection.find(query))
    
    for item in data:
        item['_id'] = str(item['_id'])
    
    return jsonify(data)

@app.route('/create-dump', methods=['POST'])
def create_dump():
    create_data_dump()
    return jsonify({"status": "success", "message": "Data dump created successfully."})

if __name__ == '__main__':
    app.run(debug=True)
