import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function AdminLogsPage() {
  const { token, user } = useAuth();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [auditLogs, setAuditLogs] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!token) return;

    const fetchLogs = async () => {
      try {
        const res = await fetch('http://localhost:8000/admin/logs', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error('Unauthorized or error fetching logs');
        const data = await res.json();
        setAuditLogs(data);
      } catch (err) {
        console.error(err);
        setError('Failed to load audit logs');
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
  }, [token]);

  if (!user || user.role !== 'admin') {
    navigate('/');
    return null;
  }

  const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;

  if (loading) return <p>Loading audit logs...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div className={`min-h-screen p-6 ${isDarkMode ? 'bg-gray-900 text-white' : 'bg-gray-100 text-black'}`}>
      <h1 className="text-3xl font-bold mb-6">Audit Logs</h1>

      <div className="overflow-x-auto bg-white dark:bg-gray-800 rounded shadow p-4">
        <table className="w-full table-auto">
          <thead>
            <tr className="bg-gray-200 dark:bg-gray-700">
              <th className="p-2 text-left">Timestamp</th>
              <th className="p-2 text-left">User</th>
              <th className="p-2 text-left">Action</th>
              <th className="p-2 text-left">Target</th>
            </tr>
          </thead>
          <tbody>
            {auditLogs.map((log) => (
              <tr key={log.id} className="hover:bg-gray-100 dark:hover:bg-gray-700">
                <td className="p-2">{new Date(log.timestamp).toLocaleString()}</td>
                <td className="p-2">{log.user_email}</td>
                <td className="p-2">{log.action}</td>
                <td className="p-2">{log.target}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
