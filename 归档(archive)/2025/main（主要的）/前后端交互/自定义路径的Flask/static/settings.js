document.addEventListener("DOMContentLoaded", function() {
    axios.get("http://127.0.0.1:5000/settings")
        .then(response => {
            document.getElementById("api_key").value = response.data.openai_api_key;
            document.getElementById("base_url").value = response.data.openai_base_url;
            document.getElementById("models").value = response.data.models;
        })
        .catch(error => console.error("Error fetching settings:", error));

    document.getElementById("saveSettings").addEventListener("click", function() {
        axios.post("http://127.0.0.1:5000/update_settings", {
            openai_api_key: document.getElementById("api_key").value,
            openai_base_url: document.getElementById("base_url").value,
            models: document.getElementById("models").value
        })
        .then(response => {
            alert("Settings updated successfully!");
            console.log(response.data);
        })
        .catch(error => console.error("Error updating settings:", error));
    });
});
