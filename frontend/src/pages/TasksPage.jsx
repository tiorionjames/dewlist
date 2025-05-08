// src/pages/TasksPage.jsx

import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const FILTERS = ['overdue', 'today', 'upcoming'];

export default function TasksPage() {
  const { token, user } = useAuth();
  const navigate = useNavigate();

  // ───────────────────────────────────────────────────────────────
  // State
  // ───────────────────────────────────────────────────────────────
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState('');

  // New-task form
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [recurrence, setRecurrence] = useState('');
  const [recurrenceEnd, setRecurrenceEnd] = useState('');

  // Edit form
  const [editingTaskId, setEditingTaskId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');

  // Pause form
  const [pausingTaskId, setPausingTaskId] = useState(null);
  const [pauseReason, setPauseReason] = useState('');

  // Roles
  const isAdmin   = user?.role === 'admin';
  const isManager = user?.role === 'manager';
  const canCreate = isAdmin || isManager;
  const canEdit   = isAdmin || isManager;
  const canDelete = isAdmin;

  // ───────────────────────────────────────────────────────────────
  // Load tasks
  // ───────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!token) return;
    let url = 'http://localhost:8000/tasks';
    if (filter) url += `?due=${filter}`;
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => {
        if (!res.ok) throw new Error('Unauthorized');
        return res.json();
      })
      .then(data => setTasks(data))
      .catch(err => console.error('Fetch tasks error:', err));
  }, [token, filter]);

  // ───────────────────────────────────────────────────────────────
  // Handlers
  // ───────────────────────────────────────────────────────────────

  async function handleCreate(e) {
    e.preventDefault();
    const payload = {
      title,
      description: description || undefined,
      due_date: dueDate ? `${dueDate}T00:00:00` : undefined,
      recurrence: recurrence || undefined,
      recurrence_end: recurrenceEnd ? `${recurrenceEnd}T00:00:00` : undefined,
    };
    try {
      const res = await fetch('http://localhost:8000/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error();
      const newTask = await res.json();
      setTasks(prev => [newTask, ...prev]);
      setTitle(''); setDescription(''); setDueDate(''); setRecurrence(''); setRecurrenceEnd('');
    } catch {
      alert('Could not create task');
    }
  }

  async function handleStart(id) {
    try {
      const res = await fetch(`http://localhost:8000/tasks/${id}/start`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error();
      const updated = await res.json();
      setTasks(prev => prev.map(t => t.id === updated.id ? updated : t));
    } catch {
      alert('Could not start task');
    }
  }

  async function handleEnd(id) {
    try {
      const res = await fetch(`http://localhost:8000/tasks/${id}/end`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error();
      const updated = await res.json();
      setTasks(prev => prev.map(t => t.id === updated.id ? updated : t));
    } catch {
      alert('Could not end task');
    }
  }

  function startPause(id) {
    setPausingTaskId(id);
    setPauseReason('');
  }

  async function handlePause(e) {
    e.preventDefault();
    try {
      const res = await fetch(`http://localhost:8000/tasks/${pausingTaskId}/pause`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ reason: pauseReason }),
      });
      if (!res.ok) throw new Error();
      const updated = await res.json();
      setTasks(prev => prev.map(t => t.id === updated.id ? updated : t));
      setPausingTaskId(null);
      setPauseReason('');
    } catch {
      alert('Could not pause task');
    }
  }

  async function handleResume(id) {
    try {
      const res = await fetch(`http://localhost:8000/tasks/${id}/resume`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error();
      const updated = await res.json();
      setTasks(prev => prev.map(t => t.id === updated.id ? updated : t));
    } catch {
      alert('Could not resume task');
    }
  }

  async function handleToggleComplete(id) {
    try {
      const res = await fetch(`http://localhost:8000/tasks/${id}/complete`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error();
      const updated = await res.json();
      setTasks(prev => prev.map(t => t.id === updated.id ? updated : t));
    } catch {
      alert('Could not toggle complete');
    }
  }

  async function handleEdit(id) {
    if (!editTitle && !editDescription) return;
    try {
      const res = await fetch(`http://localhost:8000/tasks/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ title: editTitle, description: editDescription }),
      });
      if (!res.ok) throw new Error();
      const updated = await res.json();
      setTasks(prev => prev.map(t => t.id === id ? updated : t));
      setEditingTaskId(null);
      setEditTitle(''); setEditDescription('');
    } catch {
      alert('Could not update task');
    }
  }

  async function handleDelete(id) {
    if (!window.confirm('Delete this task?')) return;
    try {
      const res = await fetch(`http://localhost:8000/tasks/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error();
      setTasks(prev => prev.filter(t => t.id !== id));
    } catch {
      alert('Could not delete task');
    }
  }

  // ───────────────────────────────────────────────────────────────
  // JSX
  // ───────────────────────────────────────────────────────────────
  return (
    <div className="p-4 max-w-3xl mx-auto">
      {/* Dashboard Nav */}
      <div className="flex gap-2 mb-6">
        {isAdmin && (
          <button
            onClick={() => navigate('/admin')}
            className="px-4 py-2 bg-indigo-500 text-white rounded"
          >Admin Dashboard</button>
        )}
        {isManager && (
          <button
            onClick={() => navigate('/manager/dashboard')}
            className="px-4 py-2 bg-indigo-500 text-white rounded"
          >Manager Dashboard</button>
        )}
      </div>

      <h1 className="text-2xl font-bold mb-4">Your Tasks</h1>

      {/* New Task Form */}
      {canCreate && (
        <form onSubmit={handleCreate} className="mb-6 p-4 border rounded space-y-3">
          <h2 className="text-xl">New Task</h2>
          <input
            type="text" value={title}
            onChange={e => setTitle(e.target.value)}
            placeholder="Title"
            className="w-full border p-2 rounded"
            required
          />
          <textarea
            value={description}
            onChange={e => setDescription(e.target.value)}
            placeholder="Description (optional)"
            className="w-full border p-2 rounded"
          />
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm">Due Date</label>
              <input
                type="date" value={dueDate}
                onChange={e => setDueDate(e.target.value)}
                className="w-full border p-2 rounded"
              />
            </div>
            <div>
              <label className="block text-sm">Recurrence</label>
              <select
                value={recurrence}
                onChange={e => setRecurrence(e.target.value)}
                className="w-full border p-2 rounded"
              >
                <option value="">None</option>
                {FILTERS.map(f => (
                  <option key={f} value={f}>
                    {f.charAt(0).toUpperCase() + f.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            {recurrence && (
              <div className="col-span-2">
                <label className="block text-sm">Recurrence End</label>
                <input
                  type="date" value={recurrenceEnd}
                  onChange={e => setRecurrenceEnd(e.target.value)}
                  className="w-full border p-2 rounded"
                />
              </div>
            )}
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-green-500 text-white rounded"
          >Create Task</button>
        </form>
      )}

      {/* Filter */}
      <div className="mb-6">
        <label className="mr-2">Filter:</label>
        <select
          value={filter}
          onChange={e => setFilter(e.target.value)}
          className="border p-1 rounded"
        >
          <option value="">All</option>
          {FILTERS.map(f => (
            <option key={f} value={f}>
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Tasks Grid */}
      {tasks.length === 0 ? (
        <p>No tasks found.</p>
      ) : (
        <div className="grid gap-4">
          {tasks.map(t => (
            <div
              key={t.id}
              className="p-4 border rounded shadow-sm hover:shadow-md transition"
            >
              <h3 className="font-semibold text-lg">{t.title}</h3>
              {t.description && <p className="text-sm mb-2">{t.description}</p>}

              {/* Timestamps */}
              <div className="text-xs text-gray-600 space-y-1 mb-2">
                {t.start_time   && <div>Started:   {new Date(t.start_time).toLocaleString()}</div>}
                {t.paused_at    && <div>Paused:    {new Date(t.paused_at).toLocaleString()}</div>}
                {t.resumed_at   && <div>Resumed:   {new Date(t.resumed_at).toLocaleString()}</div>}
                {t.end_time     && <div>Ended:     {new Date(t.end_time).toLocaleString()}</div>}
                {t.completed_at && <div>Completed: {new Date(t.completed_at).toLocaleString()}</div>}
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-2 mb-2">
                <button onClick={() => handleStart(t.id)}      className="px-2 py-1 bg-blue-100 rounded">Start</button>
                <button onClick={() => startPause(t.id)}        className="px-2 py-1 bg-yellow-100 rounded">Pause</button>
                <button onClick={() => handleResume(t.id)}     className="px-2 py-1 bg-yellow-300 rounded">Resume</button>
                <button onClick={() => handleToggleComplete(t.id)} className="px-2 py-1 bg-green-100 rounded">
                  {t.is_complete ? 'Undo' : 'Complete'}
                </button>
                <button onClick={() => handleEnd(t.id)}        className="px-2 py-1 bg-blue-200 rounded">End</button>

                {/* Edit form/button */}
                {editingTaskId === t.id ? (
                  <form onSubmit={() => handleEdit(t.id)} className="space-y-2">
                    <input
                      value={editTitle}
                      onChange={e => setEditTitle(e.target.value)}
                      placeholder="New title"
                      className="border p-1 rounded"
                    />
                    <textarea
                      value={editDescription}
                      onChange={e => setEditDescription(e.target.value)}
                      placeholder="New description"
                      className="border p-1 rounded w-full"
                    />
                    <button type="submit" className="px-2 py-1 bg-blue-500 text-white rounded">Save</button>
                    <button
                      type="button"
                      onClick={() => setEditingTaskId(null)}
                      className="px-2 py-1 bg-gray-300 rounded ml-2"
                    >Cancel</button>
                  </form>
                ) : (
                  canEdit && (
                    <button
                      onClick={() => {
                        setEditingTaskId(t.id);
                        setEditTitle(t.title);
                        setEditDescription(t.description || '');
                      }}
                      className="px-2 py-1 bg-indigo-200 rounded"
                    >Edit</button>
                  )
                )}

                {canDelete && (
                  <button onClick={() => handleDelete(t.id)} className="px-2 py-1 bg-red-200 rounded">Delete</button>
                )}
              </div>

              {/* Pause Form */}
              {pausingTaskId === t.id && (
                <form onSubmit={handlePause} className="mt-2 space-y-2">
                  <textarea
                    value={pauseReason}
                    onChange={e => setPauseReason(e.target.value)}
                    placeholder="Reason for pause"
                    className="w-full border p-2 rounded"
                    required
                  />
                  <div className="flex gap-2">
                    <button type="submit" className="px-3 py-1 bg-yellow-500 text-white rounded">Submit Pause</button>
                    <button type="button" onClick={() => setPausingTaskId(null)} className="px-3 py-1 bg-gray-300 rounded">Cancel</button>
                  </div>
                </form>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
