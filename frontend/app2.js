// Simple front‑end logic for Workflow Company OS

// Determine the API base. If running locally (served from file or a different port), default to localhost:8000.
const API_BASE = (window.location.hostname === 'localhost' || window.location.hostname === '') ? 'http://localhost:8000' : window.location.origin;

// Handle employee form submission
document.getElementById('employee-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('name').value;
    const role = document.getElementById('role').value;
    const department = document.getElementById('department').value;
    const salary = parseFloat(document.getElementById('salary').value);
    const bank = document.getElementById('bank').value;
    const payload = {
        name: name,
        role: role || null,
        department: department || null,
        salary: salary,
        bank_account: bank || null
    };
    try {
        const res = await fetch(`${API_BASE}/employees`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) {
            throw new Error('Failed to create employee');
        }
        const data = await res.json();
        document.getElementById('employee-msg').textContent = `Employee created: ID ${data.id}`;
        // Reset form and refresh list
        e.target.reset();
        loadEmployees();
    } catch (err) {
        document.getElementById('employee-msg').textContent = err.message;
    }
});

// Fetch and display all employees
async function loadEmployees() {
    const tbody = document.querySelector('#employees-table tbody');
    tbody.innerHTML = '';
    try {
        const res = await fetch(`${API_BASE}/employees`);
        const employees = await res.json();
        if (employees.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6">No employees found.</td></tr>';
            return;
        }
        employees.forEach((emp) => {
            const row = document.createElement('tr');
            row.innerHTML = `<td>${emp.id}</td><td>${emp.name}</td><td>${emp.role || ''}</td><td>${emp.department || ''}</td><td>${emp.salary}</td><td>${emp.status}</td>`;
            tbody.appendChild(row);
        });
    } catch (err) {
        tbody.innerHTML = '<tr><td colspan="6">Failed to load employees</td></tr>';
    }
}

// Preview payroll for selected month/year
async function previewPayroll() {
    const month = parseInt(document.getElementById('month').value);
    const year = parseInt(document.getElementById('year').value);
    const previewDiv = document.getElementById('payroll-preview');
    previewDiv.innerHTML = '';
    try {
        const res = await fetch(`${API_BASE}/payroll/preview?month=${month}&year=${year}`);
        if (!res.ok) throw new Error('Failed to preview payroll');
        const preview = await res.json();
        if (!preview.items || preview.items.length === 0) {
            previewDiv.innerHTML = '<p>No payroll data available. Add employees first.</p>';
            return;
        }
        // Display preview summary
        let html = '<p><strong>Total cost:</strong> ' + preview.total_cost + '</p>';
        html += '<table><thead><tr><th>Employee</th><th>Gross</th><th>Deductions</th><th>Net</th></tr></thead><tbody>';
        preview.items.forEach(item => {
            html += `<tr><td>${item.name}</td><td>${item.gross}</td><td>${item.deductions}</td><td>${item.net}</td></tr>`;
        });
        html += '</tbody></table>';
        html += '<button id="approve-btn">Approve Payroll</button>';
        previewDiv.innerHTML = html;
        document.getElementById('approve-btn').addEventListener('click', () => approvePayroll(month, year));
    } catch (err) {
        previewDiv.textContent = err.message;
    }
}

// Approve payroll for selected period
async function approvePayroll(month, year) {
    const previewDiv = document.getElementById('payroll-preview');
    try {
        const res = await fetch(`${API_BASE}/payroll/approve?month=${month}&year=${year}`, {
            method: 'POST'
        });
        if (!res.ok) throw new Error('Failed to approve payroll');
        const data = await res.json();
        previewDiv.innerHTML += '<p>Payroll approved! ID: ' + data.payroll_id + '</p>';
        loadEmployees();
    } catch (err) {
        previewDiv.innerHTML += '<p>' + err.message + '</p>';
    }
}

// Initial load of employees on page ready
loadEmployees();
