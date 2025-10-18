const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

const BACKEND = process.env.BACKEND_URL || 'http://backend:8000';

app.get('/', (req, res) => {
  res.json({ message: 'Sacred QA Frontend', status: 'running' });
});

app.get('/sankalpas', async (req, res) => {
  try {
    const response = await fetch(`${BACKEND}/sankalpa`);
    const data = await response.json();
    
    res.send(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Sankalpas</title>
        <style>
          body { font-family: system-ui; padding: 20px; }
          table { border-collapse: collapse; width: 100%; margin-top: 20px; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
          th { background: #f4f4f4; }
          a { color: #0066cc; }
          input { padding: 8px; width: 300px; margin-bottom: 10px; }
        </style>
      </head>
      <body>
        <a href="/">← Home</a>
        <h1>Sankalpas (${data.length})</h1>
        <input type="text" id="search" placeholder="Filter by text..." onkeyup="filterTable()">
        <table id="dataTable">
          <thead>
            <tr>
              <th>ID</th>
              <th>Text</th>
              <th>Context</th>
              <th>Status</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            ${data.map(s => `
              <tr>
                <td>${s.id.slice(0, 8)}</td>
                <td>${s.text}</td>
                <td>${s.context || ''}</td>
                <td>${s.status || ''}</td>
                <td>${new Date(s.created_at).toLocaleString()}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
        <script>
          function filterTable() {
            const input = document.getElementById('search');
            const filter = input.value.toLowerCase();
            const table = document.getElementById('dataTable');
            const rows = table.getElementsByTagName('tr');
            
            for (let i = 1; i < rows.length; i++) {
              const textCell = rows[i].getElementsByTagName('td')[1];
              if (textCell) {
                const text = textCell.textContent || textCell.innerText;
                rows[i].style.display = text.toLowerCase().indexOf(filter) > -1 ? '' : 'none';
              }
            }
          }
        </script>
      </body>
      </html>
    `);
  } catch (error) {
    res.status(500).send(`Error: ${error.message}`);
  }
});

app.get('/logs', async (req, res) => {
  try {
    const response = await fetch(`${BACKEND}/qa_logs`);
    const data = await response.json();
    
    res.send(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>QA Logs</title>
        <style>
          body { font-family: system-ui; padding: 20px; }
          table { border-collapse: collapse; width: 100%; margin-top: 20px; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }
          th { background: #f4f4f4; }
          a { color: #0066cc; }
          pre { background: #f8f8f8; padding: 8px; overflow-x: auto; max-width: 400px; }
          details { cursor: pointer; }
        </style>
      </head>
      <body>
        <a href="/">← Home</a>
        <h1>QA Logs (${data.length})</h1>
        <p>Auto-refresh: <button onclick="location.reload()">Refresh Now</button></p>
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Agent</th>
              <th>Model</th>
              <th>Device</th>
              <th>Request</th>
              <th>Response</th>
            </tr>
          </thead>
          <tbody>
            ${data.map(log => `
              <tr>
                <td>${new Date(log.created_at).toLocaleString()}</td>
                <td>${log.agent_id}</td>
                <td>${log.model || ''}</td>
                <td>${log.device || ''}</td>
                <td><pre>${JSON.stringify(log.request_json, null, 2)}</pre></td>
                <td>
                  <details>
                    <summary>View</summary>
                    <pre>${JSON.stringify(log.response_json, null, 2)}</pre>
                  </details>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
        <script>setTimeout(() => location.reload(), 10000);</script>
      </body>
      </html>
    `);
  } catch (error) {
    res.status(500).send(`Error: ${error.message}`);
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Frontend on :${PORT}`);
});
