// signup.js
// Handle admin signup form submission

document.getElementById('signup-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('signup-email').value.trim();
  const password = document.getElementById('signup-password').value;
  const errorEl = document.getElementById('error');
  errorEl.textContent = '';
  try {
    const res = await fetch('http://localhost:8000/auth/admin/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, role: 'admin' })
    });
    const data = await res.json();
    if (!res.ok) {
      // Display error message from server if available
      errorEl.textContent = data.detail || 'Signup failed';
      return;
    }
    // Save token and role
    localStorage.setItem('token', data.token);
    // Fetch current user to determine role
    const userRes = await fetch('http://localhost:8000/users/me', {
      headers: { 'Authorization': 'Bearer ' + data.token }
    });
    const user = await userRes.json();
    localStorage.setItem('role', user.role);
    // Redirect to admin dashboard
    window.location.href = 'admin.html';
  } catch (err) {
    errorEl.textContent = err.message;
  }
});
