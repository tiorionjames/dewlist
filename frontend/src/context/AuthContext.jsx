// src/context/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [user, setUser]   = useState(null);

  // helper to fetch /users/me
  const fetchCurrentUser = async (t) => {
    try {
      const res = await fetch('http://localhost:8000/users/me', {
        headers: { Authorization: `Bearer ${t}` },
      });
      if (!res.ok) throw new Error('Failed to fetch user');
      const me = await res.json();
      setUser(me);
    } catch {
      // invalid token → force logout
      logout();
    }
  };

  const login = async (newToken) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    await fetchCurrentUser(newToken);  // load the user right away
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  // on mount, if we already have a token, load the user
  useEffect(() => {
    if (token) fetchCurrentUser(token);
  }, []);

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
