const { DefaultAzureCredential } = require("@azure/identity");
const { DigitalTwinsClient } = require("@azure/digital-twins-core");

module.exports = async function (context, eventHubMessages) {
    context.log("IoT Hub trigger function processing a message.");

    const messages = Array.isArray(eventHubMessages) ? eventHubMessages : [eventHubMessages];

    const adtInstanceUrl = "https://DHT22Mazen.api.eus2.digitaltwins.azure.net"; // Replace with your ADT instance URL
    const digitalTwinId = "AmnaRaspberryPi"; // Your digital twin ID

    const credential = new DefaultAzureCredential();
    const client = new DigitalTwinsClient(adtInstanceUrl, credential);

    for (const message of messages) {
        const payload = typeof message === "string" ? JSON.parse(message) : message;

        context.log("Received message:", JSON.stringify(payload));

        const temperature = payload.temperature;
        const humidity = payload.humidity;

        if (temperature === undefined || humidity === undefined) {
            context.log.error("Missing temperature or humidity in payload.");
            continue;
        }

        context.log(`Updating digital twin '${digitalTwinId}' with temp: ${temperature}, humidity: ${humidity}`);

        const patch = [
            { op: "replace", path: "/temperature", value: temperature },
            { op: "replace", path: "/humidity", value: humidity }
        ];

        try {
            await client.updateDigitalTwin(digitalTwinId, patch);
            context.log("Digital twin updated successfully.");
        } catch (err) {
            context.log.error("Failed to update digital twin:", err.message);
        }
    }
};
