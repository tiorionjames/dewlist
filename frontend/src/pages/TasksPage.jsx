// src/pages/TasksPage.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const FILTERS = ['overdue', 'today', 'upcoming'];

export default function TasksPage() {
  const { token, user } = useAuth();
  const navigate = useNavigate();

  // State
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState('');

  // New Task Form
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [recurrence, setRecurrence] = useState('');
  const [recurrenceEnd, setRecurrenceEnd] = useState('');

  // Edit & Pause
  const [editingTaskId, setEditingTaskId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [pausingTaskId, setPausingTaskId] = useState(null);
  const [pauseReason, setPauseReason] = useState('');

  // Permissions
  const isAdmin   = user?.role === 'admin';
  const isManager = user?.role === 'manager';
  const canCreate = isAdmin || isManager;
  const canEdit   = isAdmin || isManager;
  const canDelete = isAdmin;

  // Fetch tasks
  useEffect(() => {
    if (!token) return;
    let url = 'http://localhost:8000/tasks';
    if (filter) url += `?due=${filter}`;
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => res.ok ? res.json() : Promise.reject('Unauthorized'))
      .then(setTasks)
      .catch(console.error);
  }, [token, filter]);

  // Create
  const handleCreate = async e => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          title,
          description: description || undefined,
          due_date: dueDate ? `${dueDate}T00:00:00` : undefined,
          recurrence: recurrence || undefined,
          recurrence_end: recurrenceEnd ? `${recurrenceEnd}T00:00:00` : undefined,
        }),
      });
      if (!res.ok) throw new Error();
      const newTask = await res.json();
      setTasks(prev => [newTask, ...prev]);
      setTitle(''); setDescription(''); setDueDate(''); setRecurrence(''); setRecurrenceEnd('');
    } catch {
      alert('Could not create task');
    }
  };

  // Generic action (start, pause, resume, complete, end, delete)
  const handleAction = async (id, action, payload = null) => {
    try {
      const res = await fetch(`http://localhost:8000/tasks/${id}/${action}`, {
        method: action === 'delete' ? 'DELETE' : 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
          ...(payload && { 'Content-Type': 'application/json' }),
        },
        body: payload ? JSON.stringify(payload) : undefined,
      });
      if (!res.ok) throw new Error();
      if (action === 'delete') {
        setTasks(prev => prev.filter(t => t.id !== id));
      } else {
        const updated = await res.json();
        setTasks(prev => prev.map(t => t.id === updated.id ? updated : t));
        if (action === 'pause') setPausingTaskId(null);
      }
    } catch {
      alert(`Could not ${action} task`);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-12">
      {/* Navigation */}
      <div className="flex gap-4">
        {isAdmin   && (
          <button
            onClick={() => navigate('/admin')}
            className="px-4 py-2 bg-indigo-500 text-white rounded"
          >
            Admin Dashboard
          </button>
        )}
        {isManager && (
          <button
            onClick={() => navigate('/manager/dashboard')}
            className="px-4 py-2 bg-indigo-500 text-white rounded"
          >
            Manager Dashboard
          </button>
        )}
      </div>

      {/* New Task Form */}
      {canCreate && (
  <form
    onSubmit={handleCreate}
    className="border p-6 rounded-lg space-y-4 max-w-lg mx-auto"
  >
    <h2 className="text-2xl font-bold text-primary">New Task</h2>
    <input
      className="w-full border p-2 rounded"
      placeholder="Title"
            value={title}
            onChange={e => setTitle(e.target.value)}
            required
          />
          <textarea
            className="w-full border p-2 rounded"
            placeholder="Description (optional)"
            value={description}
            onChange={e => setDescription(e.target.value)}
          />
          <div className="grid grid-cols-2 gap-4">
            {/* Due Date */}
            <div>
              <label className="block text-sm mb-1">Due Date</label>
              <input
                type="date"
                className="w-full border p-2 rounded"
                value={dueDate}
                onChange={e => setDueDate(e.target.value)}
              />
            </div>
            {/* Recurrence */}
            <div>
              <label className="block text-sm mb-1">Recurrence</label>
              <select
                className="w-full border p-2 rounded"
                value={recurrence}
                onChange={e => setRecurrence(e.target.value)}
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
                <label className="block text-sm mb-1">Recurrence End</label>
                <input
                  type="date"
                  className="w-full border p-2 rounded"
                  value={recurrenceEnd}
                  onChange={e => setRecurrenceEnd(e.target.value)}
                />
              </div>
            )}
          </div>
          <button type="submit" className="px-6 py-2 bg-green-500 text-white rounded-lg">
            Create Task
          </button>
        </form>
      )}

      {/* Filter Controls */}
      <div className="flex items-center gap-2">
        <label>Filter:</label>
        <select
          className="border p-2 rounded"
          value={filter}
          onChange={e => setFilter(e.target.value)}
        >
          <option value="">All</option>
          {FILTERS.map(f => (
            <option key={f} value={f}>
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Task Cards Grid */}
      <div>
        <h1 className="text-3xl font-bold mb-6 text-white">Your Tasks</h1>

        {tasks.length === 0 ? (
          <p className="text-gray-400">No tasks found.</p>
        ) : (
          <div className="task-grid"> {/* CHANGED: single wrapper */}
            {tasks.map(task => (
              <div
                key={task.id}
                className="task-card flex flex-col justify-between" /* CHANGED: your scoped card */
              >
                <div className="space-y-3 text-white">
                  <h3 className="text-xl font-semibold">{task.title}</h3>
                  {task.description && (
                    <p className="text-sm text-gray-300">{task.description}</p>
                  )}
                  <div className="text-xs text-gray-500 space-y-1">
                    {task.start_time   && <div>Started:   {new Date(task.start_time).toLocaleString()}</div>}
                    {task.paused_at    && <div>Paused:    {new Date(task.paused_at).toLocaleString()}</div>}
                    {task.resumed_at   && <div>Resumed:   {new Date(task.resumed_at).toLocaleString()}</div>}
                    {task.end_time     && <div>Ended:     {new Date(task.end_time).toLocaleString()}</div>}
                    {task.completed_at && <div>Completed: {new Date(task.completed_at).toLocaleString()}</div>}
                  </div>
                </div>

                <div className="flex flex-wrap gap-2 mt-4">
                  <button
                    onClick={() => handleAction(task.id, 'start')}
                    className="px-3 py-1 bg-teal-500 text-white rounded-full"
                  >
                    Start
                  </button>
                  <button
                    onClick={() => setPausingTaskId(task.id)}
                    className="px-3 py-1 bg-yellow-300 text-black rounded-full"
                  >
                    Pause
                  </button>
                  <button
                    onClick={() => handleAction(task.id, 'resume')}
                    className="px-3 py-1 bg-yellow-500 text-white rounded-full"
                  >
                    Resume
                  </button>
                  <button
                    onClick={() => handleAction(task.id, 'complete')}
                    className="px-3 py-1 bg-green-500 text-white rounded-full"
                  >
                    {task.is_complete ? 'Undo' : 'Complete'}
                  </button>
                  <button
                    onClick={() => handleAction(task.id, 'end')}
                    className="px-3 py-1 bg-red-500 text-white rounded-full"
                  >
                    End
                  </button>
                  {canEdit && (
                    <button
                      onClick={() => {
                        setEditingTaskId(task.id);
                        setEditTitle(task.title);
                        setEditDescription(task.description || '');
                      }}
                      className="px-3 py-1 bg-indigo-400 text-white rounded-full"
                    >
                      Edit
                    </button>
                  )}
                  {canEdit && editingTaskId === task.id && (
                    <button
                      onClick={() =>
                        handleAction(task.id, 'edit', { title: editTitle, description: editDescription })
                      }
                      className="px-3 py-1 bg-indigo-600 text-white rounded-full"
                    >
                      Save
                    </button>
                  )}
                  {canDelete && (
                    <button
                      onClick={() => handleAction(task.id, 'delete')}
                      className="px-3 py-1 bg-gray-600 text-white rounded-full"
                    >
                      Delete
                    </button>
                  )}
                </div>

                {pausingTaskId === task.id && (
                  <form
                    onSubmit={e => {
                      e.preventDefault();
                      handleAction(task.id, 'pause', { reason: pauseReason });
                    }}
                    className="mt-4 space-y-2"
                  >
                    <textarea
                      className="w-full border p-2 rounded"
                      placeholder="Reason for pause"
                      value={pauseReason}
                      onChange={e => setPauseReason(e.target.value)}
                      required
                    />
                    <div className="flex gap-2">
                      <button type="submit" className="px-4 py-1 bg-yellow-600 text-white rounded">
                        Submit Pause
                      </button>
                      <button
                        type="button"
                        onClick={() => setPausingTaskId(null)}
                        className="px-4 py-1 bg-gray-400 text-black rounded"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
