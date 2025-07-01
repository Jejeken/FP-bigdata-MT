from kafka import KafkaConsumer
import json
from sklearn.linear_model import LinearRegression
import numpy as np

# Model dummy
model = LinearRegression()
X_train = np.array([[10, 20], [30, 40], [50, 60]])
y_train = [50, 100, 150]
model.fit(X_train, y_train)

consumer = KafkaConsumer(
    'aqi-topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='aqi-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Mendengarkan topik Kafka...")
for message in consumer:
    data = message.value
    features = np.array([[data['pm2_5'], data['pm10']]])
    pred = model.predict(features)[0]
    print(f"Data AQI: {data}  Prediksi AQI: {pred:.2f}")

