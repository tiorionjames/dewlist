// frontend/src/pages/ForgotPasswordPage.jsx
import { useState } from 'react';
import { Link } from 'react-router-dom';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    // 🔧 Replace this URL with your real forgot-password endpoint when ready
    await fetch('http://localhost:8000/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    setSubmitted(true);
  }

  if (submitted) {
    return (
      <div className="p-4 max-w-md mx-auto">
        <h2 className="text-xl mb-4">Check Your Email</h2>
        <p>
          If an account with that email exists, you’ll receive instructions to reset your password.
        </p>
        <p className="mt-4">
          <Link to="/login" className="text-blue-500">Back to Login</Link>
        </p>
      </div>
    );
  }

  return (
    <div className="p-4 max-w-md mx-auto">
      <h2 className="text-xl mb-4">Forgot Password</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            className="w-full border p-2 rounded"
            required
          />
        </div>
        <button type="submit" className="w-full p-2 bg-red-500 text-white rounded">
          Send Reset Link
        </button>
      </form>
      <p className="mt-4">
        <Link to="/login" className="text-blue-500">Back to Login</Link>
      </p>
    </div>
  );
}
