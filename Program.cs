using MQTTnet;
using MQTTnet.Client;
using System.Text.Json; // Necessario per il JSON
using System.Text;

var mqttFactory = new MqttFactory();

using (var mqttClient = mqttFactory.CreateMqttClient())
{
    // --- CONFIGURAZIONE CONNESSIONE ---
    // Sostituirai "INSERISCI_IP_QUI" con l'IP che mi darai
    var mqttClientOptions = new MqttClientOptionsBuilder()
    .WithTcpServer("localhost", 1883) // Ora punta al tuo PC
    .Build();

    try 
    {
        await mqttClient.ConnectAsync(mqttClientOptions, CancellationToken.None);
        Console.WriteLine("Connesso al server MQTT di Node-RED!");

        // --- PREPARAZIONE DATI ---
        // Qui simuliamo i dati che poi acquisirai dal trapano
        var datiTrapano = new
        {
            PresenzaOperatore = true,      // bool
            StatoMacchina = true,         // bool
            GiriAlMinuto = 1250.5,        // double
            AssorbimentoElettrico = 4.2   // double
        };

        // Serializziamo l'oggetto in una stringa JSON
        string jsonPayload = JsonSerializer.Serialize(datiTrapano);

        // --- INVIO DATI ---
        var message = new MqttApplicationMessageBuilder()
            .WithTopic("trapano/telemetria")
            .WithPayload(jsonPayload)
            .WithQualityOfServiceLevel(MQTTnet.Protocol.MqttQualityOfServiceLevel.AtLeastOnce)
            .Build();

        await mqttClient.PublishAsync(message, CancellationToken.None);

        Console.WriteLine($"Dati inviati a Node-RED: {jsonPayload}");

        // Disconnessione pulita
        await mqttClient.DisconnectAsync();
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Errore: {ex.Message}");
    }
}