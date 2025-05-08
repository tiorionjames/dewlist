// src/components/Header.jsx
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Header() {
  const { token, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="flex justify-between p-4 bg-gray-100">
      <h1>DewList</h1>
      <nav>
        {!token ? (
          <Link to="/login">
            <button>Login</button>
          </Link>
        ) : (
          <>
            {user?.role === 'admin' && (
              <Link to="/admin">
                <button className="mr-4">Admin Dashboard</button>
              </Link>
            )}
            <button onClick={handleLogout}>Logout</button>
          </>
        )}
      </nav>
    </header>
  );
}
