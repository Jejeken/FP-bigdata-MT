from kafka import KafkaProducer
import json, time, random

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

while True:
    data = {
        'sensor_id': 'sensor-01',
        'pm2_5': round(random.uniform(10, 150), 2),
        'pm10': round(random.uniform(20, 200), 2),
    }
    print(f"Mengirim data: {data}")
    producer.send('aqi-topic', data)
    time.sleep(2)

