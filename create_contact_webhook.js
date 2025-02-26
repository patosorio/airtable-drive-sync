let inputConfig = input.config();

// Prepare data for the webhook
let data = {
    action: "create",
    record: {
        fields: {
            FullName: inputConfig.FullName,
            City: inputConfig.City,
            Country: inputConfig.Country,
            Mobile: inputConfig.Mobile,
            Email: inputConfig.Email,
            HR_ID: inputConfig.HR_ID,
            LastSynced: inputConfig.LastSynced,
            NeedsSync: inputConfig.NeedsSync
        }
    }
};

console.log("Sending data to webhook:", JSON.stringify(data, null, 2));

// Send the webhook request to Flask API
let response = await fetch("https://2a56-79-117-215-144.ngrok-free.app/webhook", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
});

if (!response.ok) {
    console.error("Failed to send webhook:", await response.text());
} else {
    console.log("Webhook sent successfully");
}