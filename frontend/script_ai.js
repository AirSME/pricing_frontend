const formData = new FormData();
formData.append("file", fileInput.files[0]);

fetch("https://n8napp-bwd3fzesc7h4hmet.southafricanorth-01.azurewebsites.net/webhook-test/upload-pricing-file", {
  method: "POST",
  headers: {
    "x-api-key": "mySuperSecretKey123"
  },
  body: formData
});
