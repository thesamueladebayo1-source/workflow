// login.js
// Handle login for admin and employee

document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  const errorEl = document.getElementById('error');
  errorEl.textContent = '';
  try {
    const res = await fetch('http://localhost:8000/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (!res.ok) {
      errorEl.textContent = data.detail || 'Login failed';
      return;
    }
    localStorage.setItem('token', data.token);
    // Determine user role
    const userRes = await fetch('http://localhost:8000/users/me', {
      headers: { 'Authorization': 'Bearer ' + data.token }
    });
    const user = await userRes.json();
    localStorage.setItem('role', user.role);
    // Redirect based on role
    if (user.role === 'admin') {
      window.location.href = 'admin.html';
    } else {
      window.location.href = 'employee.html';
    }
  } catch (err) {
    errorEl.textContent = err.message;
  }
});
