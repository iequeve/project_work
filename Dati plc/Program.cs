using MQTTnet;
using MQTTnet.Client;
using System.Text.Json;
using System.Text;
using System.Collections.Generic;
using System.IO;
using TwinCAT.Ads; // Libreria ufficiale Beckhoff

// Classe per rappresentare una variabile
class Variable
{
    public string name { get; set; }
    public bool isArray { get; set; } = false;
}

class Program
{
    // Variabili di configurazione
    static string addressMqttBroker = "";
    static int portMqtt = 0;
    static string topicMqtt = "";
    static string amsNetId = "";
    static int portAds = 0;
    static int cycleTimeMs = 5000;
    static List<Variable> variablesList = new List<Variable>();

    static async Task Main()
    {
        //funzione di estrazione della configurazione dal file json
        InizializzaConfigurazione("conf.json");

        while (true)
        {
            var datiLettiDalPlc = new Dictionary<string, object>();

            try
            {
                // Connessione ADS
                using (AdsClient adsClient = new AdsClient())
                {
                    Console.WriteLine($"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] Connessione ADS a {amsNetId}:{portAds}...");
                    adsClient.Connect(amsNetId, portAds);

                    foreach (var variable in variablesList)
                    {
                        try
                        {
                            string varName = variable.name;
                            object valore = null;

                            if (variable.isArray)
                            {
                                // Se è un array, leggi il primo elemento
                                varName = $"{variable.name}[0]";
                                valore = adsClient.ReadValue(varName, typeof(int));
                                Console.WriteLine($"Letta variabile array {variable.name}[0]: {valore}");
                            }
                            else
                            {
                                // Lettura di una variabile scalare
                                valore = adsClient.ReadValue(varName, typeof(int));
                                Console.WriteLine($"Letta variabile {varName}: {valore}");
                            }

                            datiLettiDalPlc.Add(variable.name, valore);
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine($"Errore nella lettura di {variable.name}: {ex.Message}");
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

            // Attesa prima del prossimo ciclo
            Console.WriteLine($"Prossimo ciclo tra {cycleTimeMs}ms...\n");
            await Task.Delay(cycleTimeMs);
        }
    }

    //funzione di estrazione della configurazione dal file json
    static void InizializzaConfigurazione(string filePath)
    {
        string jsonString = File.ReadAllText(filePath);
        using (JsonDocument doc = JsonDocument.Parse(jsonString))
        {
            JsonElement root = doc.RootElement;

            // Tempo di ciclo
            if (root.TryGetProperty("cycle_time_ms", out var cycleElement))
            {
                cycleTimeMs = cycleElement.GetInt32();
            }

            // Configurazione MQTT
            JsonElement mqttConfig = root.GetProperty("mqtt_config");
            addressMqttBroker = mqttConfig.GetProperty("address_mqttBroker").GetString() ?? "";
            portMqtt = mqttConfig.GetProperty("port_mqtt").GetInt32();
            topicMqtt = mqttConfig.GetProperty("topic_mqtt").GetString() ?? "";

            // Configurazione PLC Beckhoff (ADS)
            JsonElement plcConfig = root.GetProperty("plc_config");
            amsNetId = plcConfig.GetProperty("ams_netId").GetString() ?? ""; // Es: "192.168.1.10.1.1"
            portAds = plcConfig.GetProperty("port_ads").GetInt32();     // Di solito 851 per TwinCAT 3

            // Estrazione lista variabili
            variablesList = new List<Variable>();
            foreach (JsonElement v in root.GetProperty("variables").EnumerateArray())
            {
                var variable = new Variable
                {
                    name = v.GetProperty("name").GetString() ?? "",
                    isArray = v.TryGetProperty("isArray", out var isArrayElement) ? isArrayElement.GetBoolean() : false
                };
                variablesList.Add(variable);
            }
        }
    }
}