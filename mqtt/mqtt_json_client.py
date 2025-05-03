
import paho.mqtt.client as mqtt
import xml.etree.ElementTree as ET
import json

# === LECTURE DU FICHIER CONFIG XML ===
def read_config(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    config = {
        "broker_url": root.find("broker_url").text,
        "port": int(root.find("port").text),
        "location": root.find("location").text,
        "topics": [topic.text for topic in root.find("topics").findall("topic")]
    }
    return config

# === CALLBACKS MQTT ===
def on_connect(client, userdata, flags, rc):
    print("✅ Connecté au broker avec le code :", rc)
    for topic in userdata["topics"]:
        client.subscribe(topic)
        print(f"📡 Abonné à : {topic}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        print(f"📥 Message reçu sur [{msg.topic}] : {json.dumps(data, indent=2)}")
    except json.JSONDecodeError:
        print(f"❌ Message non-JSON reçu sur [{msg.topic}] : {msg.payload.decode()}")

# === FONCTION PRINCIPALE ===
def main():
    config = read_config("mqtt_config_example.xml")

    client = mqtt.Client(userdata=config)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(config["broker_url"], config["port"], 60)
    client.loop_start()

    print("✉️ Entrez un topic (ou tapez 'exit' pour quitter) :")
    while True:
        topic = input("Topic > ")
        if topic.lower() == "exit":
            break
        if topic not in config["topics"]:
            print("⚠️ Ce topic n'est pas dans la liste de souscription.")
            continue
        try:
            message = input("Message JSON > ")
            json_obj = json.loads(message)  # Valide le format JSON
            client.publish(topic, json.dumps(json_obj))
        except Exception as e:
            print("Erreur de format JSON :", e)

    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    main()
