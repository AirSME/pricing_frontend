window.addEventListener('beforeunload', () => {
  console.log("Page is reloading...");
});

//DOM loaded 
document.addEventListener('DOMContentLoaded', () => {
  console.log("script.js loaded");
  const messageDiv = document.getElementById('message');
  const uploadButton = document.getElementById('uploadButton');
  const cleanButton = document.getElementById('cleanBtn');
  const downloadButton = document.getElementById('downloadBtn');
  const fileInput = document.getElementById('fileInput');


//upload button clicked
uploadButton.addEventListener('click', async (event) => { 
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
      const result = await response.json();
      console.log("Response:", result);

      if (response.ok) {
        messageDiv.innerText = `File uploaded: ${result.filename}`;
        messageDiv.style.color = 'green';
        fileInput.value = '';
        cleanButton.disabled = false;
        window.currentFilename = result.filename;
      } else {
        messageDiv.innerText = `Error: ${result.error}`;
        messageDiv.style.color = 'red';
      }
    } catch (error) {
      messageDiv.innerText = `Upload failed: ${error.message}`;
      messageDiv.style.color = 'red';
    }
  });

//clean button clicked
  cleanButton.addEventListener('click', async () => {
    messageDiv.innerText = 'Cleaning file...';
    messageDiv.style.color = 'black';

    try {
      const response = await fetch('http://localhost:5050/excel_formatter/clean', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ filename: window.currentFilename })  
});

      const result = await response.json();
      console.log("Clean response:", result);

      if (response.ok) {
        messageDiv.innerText = `File cleaned. Download Ready`;
        messageDiv.style.color = 'green';
        downloadButton.disabled = false;
        window.cleanedFilename = result.filename;
      } else {
        messageDiv.innerText = `Cleaning failed: ${result.error}`;
        messageDiv.style.color = 'red';
      }
    } catch (error) {
      messageDiv.innerText = `Cleaning request failed: ${error.message}`;
      messageDiv.style.color = 'red';
    }
  });

//download button clicked  
  downloadButton.addEventListener('click', () => {
    if (!window.cleanedFilename) {
    messageDiv.innerText = "No cleaned file available.";
    messageDiv.style.color = "red";
    return;
  } 
    const downloadLink = document.createElement('a');
    downloadLink.href = `http://localhost:5050/excel_formatter/download?filename=${encodeURIComponent(window.cleanedFilename)}`;
    downloadLink.download = window.cleanedFilename;
    downloadLink.click();
    messageDiv.innerText = 'File downloaded successfully';
    messageDiv.style.color = 'red';
  });
});

