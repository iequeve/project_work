using MQTTnet;
using MQTTnet.Client;
using System.Text.Json;
using System.Text;
using System.Collections.Generic;
using System.IO;
using TwinCAT.Ads; // Libreria ufficiale Beckhoff

// Variabili di configurazione
string addressMqttBroker;
int portMqtt = 0;
string topicMqtt;
// Configurazione ADS
string amsNetId;
int portAds = 0;
//array delle variabili da erichiedere al PLC
string[] variablesArray;




//funzione diu estrazione della configurazione dal file json
void InizializzaConfigurazione(string filePath)
{
    string jsonString = File.ReadAllText(filePath);
    using (JsonDocument doc = JsonDocument.Parse(jsonString))
    {
        JsonElement root = doc.RootElement;

        // Configurazione MQTT, da warning perché teme di avere variabili nulle
        JsonElement mqttConfig = root.GetProperty("mqtt_config");
        addressMqttBroker = mqttConfig.GetProperty("address_mqttBroker").GetString();
        portMqtt = mqttConfig.GetProperty("port_mqtt").GetInt32();
        topicMqtt = mqttConfig.GetProperty("topic_mqtt").GetString();

        // Configurazione PLC Beckhoff (ADS), da warning perché teme di avere variabili nulle
        JsonElement plcConfig = root.GetProperty("plc_config");
        amsNetId = plcConfig.GetProperty("ams_netId").GetString(); // Es: "192.168.1.10.1.1"
        portAds = plcConfig.GetProperty("port_ads").GetInt32();     // Di solito 851 per TwinCAT 3

        // Estrazione lista variabili
        List<string> listaTemporanea = new List<string>();
        foreach (JsonElement v in root.GetProperty("variables").EnumerateArray())
        {
            listaTemporanea.Add(v.GetString());
        }
        variablesArray = listaTemporanea.ToArray();
    }
}




//parte principale del programma
try
{
    InizializzaConfigurazione("conf.json");

    var datiLettiDalPlc = new Dictionary<string, object>();

    // Connessione ADS
    using (AdsClient adsClient = new AdsClient())
    {
        Console.WriteLine($"Connessione ADS a {amsNetId}:{portAds}...");
        adsClient.Connect(amsNetId, portAds);

        foreach (var varName in variablesArray)
        {
            try
            {
                // Lettura dinamica: assumiamo siano variabili di tipo INT (short) o DINT (int)
                // Usiamo ReadValue per leggere direttamente tramite il nome della variabile
                var valore = adsClient.ReadValue(varName, typeof(int)); 
                datiLettiDalPlc.Add(varName, valore);
                Console.WriteLine($"Letta variabile {varName}: {valore}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Errore nella lettura di {varName}: {ex.Message}");
            }
        }
        adsClient.Disconnect();
    }

    //invio dei dati tramite MQTT
    var mqttFactory = new MqttFactory();
    using (var mqttClient = mqttFactory.CreateMqttClient())
    {
        var mqttClientOptions = new MqttClientOptionsBuilder()
            .WithTcpServer(addressMqttBroker, portMqtt)
            .Build();

        await mqttClient.ConnectAsync(mqttClientOptions, CancellationToken.None);

        string jsonPayload = JsonSerializer.Serialize(datiLettiDalPlc);

        var message = new MqttApplicationMessageBuilder()
            .WithTopic(topicMqtt)
            .WithPayload(jsonPayload)
            .WithQualityOfServiceLevel(MQTTnet.Protocol.MqttQualityOfServiceLevel.AtLeastOnce)
            .Build();


        //stampa di debug del mesaggio dati
        Console.WriteLine($"Invio a MQTT: {jsonPayload}");



        await mqttClient.PublishAsync(message, CancellationToken.None);
        Console.WriteLine($"Inviato a MQTT: {jsonPayload}");

        await mqttClient.DisconnectAsync();
    }
}
catch (Exception ex)
{
    Console.WriteLine($"Errore critico: {ex.Message}");
}