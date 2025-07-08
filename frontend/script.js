window.addEventListener('beforeunload', () => {
  console.log("Page is reloading...");
});

document.addEventListener('DOMContentLoaded', () => {
  console.log("script.js loaded");
  const uploadForm = document.getElementById('uploadForm');
  const messageDiv = document.getElementById('message');
  const cleanButton = document.getElementById('cleanBtn');
  const downloadButton = document.getElementById('downloadBtn');
  const fileInput = document.getElementById('fileInput');

console.log("Attaching submit handler to form...");  
uploadForm.addEventListener('submit', async (event) => { 
    event.preventDefault(); 
    console.log("Upload button clicked");
    const file = fileInput.files[0];
    console.log("Selected file:", file);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5050/excel_formatter/upload', {
        method: 'POST',
        body: formData
      });
      console.log("Response:", response);
      const result = await response.json();

      if (response.ok) {
        messageDiv.innerText = `File uploaded: ${result.filename}`;
        messageDiv.style.color = 'green';
        fileInput.value = '';
        cleanButton.disabled = false;
      } else {
        messageDiv.innerText = `Error: ${result.error}`;
        messageDiv.style.color = 'red';
      }
    } catch (error) {
      messageDiv.innerText = `Upload failed: ${error.message}`;
      messageDiv.style.color = 'red';
    }
  });

  cleanButton.addEventListener('click', async () => {
    messageDiv.innerText = 'Cleaning file...';
    messageDiv.style.color = 'black';

    try {
      const response = await fetch('http://localhost:5050/excel_formatter/clean', {
        method: 'POST'
      });

      const result = await response.json();

      if (response.ok) {
        messageDiv.innerText = `File cleaned. Download Ready`;
        messageDiv.style.color = 'green';
        downloadButton.disabled = false;
      } else {
        messageDiv.innerText = `Cleaning failed: ${result.error}`;
        messageDiv.style.color = 'red';
      }
    } catch (error) {
      messageDiv.innerText = `Cleaning request failed: ${error.message}`;
      messageDiv.style.color = 'red';
    }
  });

  downloadButton.addEventListener('click', () => {
    const downloadLink = document.createElement('a');
    downloadLink.href = 'http://localhost:5050/excel_formatter/download';
    downloadLink.download = 'cleaned_file.xlsx';
    downloadLink.click();
  });
});

