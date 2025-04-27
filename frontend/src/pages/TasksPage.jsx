import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

const FILTERS = ['overdue', 'today', 'upcoming'];

export default function TasksPage() {
  const { token } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState('');

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [recurrence, setRecurrence] = useState('');
  const [recurrenceEnd, setRecurrenceEnd] = useState('');

  const [editingTaskId, setEditingTaskId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');

  const [pausingTaskId, setPausingTaskId] = useState(null);
  const [pauseReason, setPauseReason] = useState('');

  useEffect(() => {
    if (token) {
      fetch('http://localhost:8000/tasks', {
        method: 'GET',
        headers: { Authorization: `Bearer ${token}` },
      })
        .then(res => res.json())
        .then(data => setTasks(data))
        .catch(err => console.error(err));
    }
  }, [token]);

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
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload),
      });
      const newTask = await res.json();
      setTasks(prev => [newTask, ...prev]);
      setTitle(''); setDescription(''); setDueDate(''); setRecurrence(''); setRecurrenceEnd('');
    } catch (err) {
      console.error('Create failed:', err);
      alert('Could not create task');
    }
  }

  async function handleDelete(id) {
    if (!window.confirm('Delete this task?')) return;
    try {
      await fetch(`http://localhost:8000/tasks/${id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } });
      setTasks(prev => prev.filter(t => t.id !== id));
    } catch (err) {
      console.error('Delete failed:', err);
      alert('Could not delete task');
    }
  }

  function startEdit(task) {
    setEditingTaskId(task.id);
    setEditTitle(task.title);
    setEditDescription(task.description || '');
  }

  function cancelEdit() {
    setEditingTaskId(null);
  }

  async function handleUpdate(e) {
    e.preventDefault();
    const payload = { title: editTitle, description: editDescription };
    try {
      const res = await fetch(`http://localhost:8000/tasks/${editingTaskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload),
      });
      const updated = await res.json();
      setTasks(prev => prev.map(t => (t.id === updated.id ? updated : t)));
      setEditingTaskId(null);
    } catch (err) {
      console.error('Update failed:', err);
      alert('Could not update task');
    }
  }

  async function handleToggleComplete(id) {
    try {
      const res = await fetch(`http://localhost:8000/tasks/${id}/complete`, { method: 'PATCH', headers: { Authorization: `Bearer ${token}` } });
      const updated = await res.json();
      setTasks(prev => prev.map(t => (t.id === updated.id ? updated : t)));
    } catch (err) {
      console.error('Toggle complete failed:', err);
      alert('Could not toggle complete');
    }
  }

  async function handleStart(id) {
    try {
      const res = await fetch(`http://localhost:8000/tasks/${id}/start`, { method: 'PATCH', headers: { Authorization: `Bearer ${token}` } });
      const updated = await res.json();
      setTasks(prev => prev.map(t => (t.id === updated.id ? updated : t)));
    } catch (err) {
      console.error('Start failed:', err);
      alert('Could not start task');
    }
  }

  async function handleEnd(id) {
    try {
      const res = await fetch(`http://localhost:8000/tasks/${id}/end`, { method: 'PATCH', headers: { Authorization: `Bearer ${token}` } });
      const updated = await res.json();
      setTasks(prev => prev.map(t => (t.id === updated.id ? updated : t)));
    } catch (err) {
      console.error('End failed:', err);
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
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ reason: pauseReason }),
      });
      const updated = await res.json();
      setTasks(prev => prev.map(t => (t.id === updated.id ? updated : t)));
      setPausingTaskId(null);
    } catch (err) {
      console.error('Pause failed:', err);
      alert('Could not pause task');
    }
  }

  async function handleResume(id) {
    try {
      const res = await fetch(`http://localhost:8000/tasks/${id}/resume`, { method: 'PATCH', headers: { Authorization: `Bearer ${token}` } });
      const updated = await res.json();
      setTasks(prev => prev.map(t => (t.id === updated.id ? updated : t)));
    } catch (err) {
      console.error('Resume failed:', err);
      alert('Could not resume task');
    }
  }

  const filteredTasks = tasks.filter(t => {
    if (!filter) return true;
    if (filter === 'overdue') return t.due_date && new Date(t.due_date) < new Date();
    if (filter === 'today') return t.due_date && new Date(t.due_date).toDateString() === new Date().toDateString();
    if (filter === 'upcoming') return t.due_date && new Date(t.due_date) > new Date();
    return true;
  });

  return (
    <div className="p-4 max-w-2xl mx-auto">
      <h1 className="text-2xl mb-4">Your Tasks</h1>

      {/* New Task Form */}
      <form onSubmit={handleCreate} className="mb-6 p-4 border rounded space-y-3">
        <h2 className="text-xl mb-2">New Task</h2>
        <input
          type="text"
          value={title}
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
              type="date"
              value={dueDate}
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
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>
        </div>
        {recurrence && (
          <div>
            <label className="block text-sm">Recurrence End</label>
            <input
              type="date"
              value={recurrenceEnd}
              onChange={e => setRecurrenceEnd(e.target.value)}
              className="w-full border p-2 rounded"
            />
          </div>
        )}
        <button type="submit" className="px-4 py-2 bg-green-500 text-white rounded">
          Create Task
        </button>
      </form>

      {/* Filter Controls */}
      <div className="mb-4">
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

      {/* Task List */}
      <ul>
        {filteredTasks.map(t => (
          <li key={t.id} className="mb-4 p-4 border rounded">
            {editingTaskId === t.id ? (
              <form onSubmit={handleUpdate} className="space-y-2">
                <input
                  value={editTitle}
                  onChange={e => setEditTitle(e.target.value)}
                  className="w-full border p-2 rounded"
                />
                <textarea
                  value={editDescription}
                  onChange={e => setEditDescription(e.target.value)}
                  className="w-full border p-2 rounded"
                />
                <div className="flex gap-2">
                  <button type="submit" className="px-3 py-1 bg-blue-500 text-white rounded">Save</button>
                  <button type="button" onClick={cancelEdit} className="px-3 py-1 bg-gray-300 rounded">Cancel</button>
                </div>
              </form>
            ) : (
              <>
                <h3 className="font-bold text-lg">{t.title}</h3>
                <p className="text-sm mb-2">{t.description}</p>
                <div className="text-xs mb-2 space-y-1">
                  {t.start_time && <div>Started: {new Date(t.start_time).toLocaleString()}</div>}
                  {t.end_time && <div>Ended: {new Date(t.end_time).toLocaleString()}</div>}
                  {t.paused_at && <div>Paused: {new Date(t.paused_at).toLocaleString()}</div>}
                  {t.resumed_at && <div>Resumed: {new Date(t.resumed_at).toLocaleString()}</div>}
                  {t.pause_reason && <div>Reason: {t.pause_reason}</div>}
                </div>
                <div className="flex flex-wrap gap-2 mb-2">
                  <button onClick={() => handleStart(t.id)} className="px-2 py-1 bg-indigo-100 rounded">Start</button>
                  <button onClick={() => handleEnd(t.id)} className="px-2 py-1 bg-indigo-200 rounded">End</button>
                  <button onClick={() => startPause(t.id)} className="px-2 py-1 bg-yellow-200 rounded">Pause</button>
                  <button onClick={() => handleResume(t.id)} className="px-2 py-1 bg-yellow-400 rounded">Resume</button>
                  <button onClick={() => handleToggleComplete(t.id)} className="px-2 py-1 bg-green-200 rounded">
                    {t.is_complete ? 'Undo' : 'Complete'}
                  </button>
                  <button onClick={() => startEdit(t)} className="px-2 py-1 bg-blue-100 rounded">Edit</button>
                  <button onClick={() => handleDelete(t.id)} className="px-2 py-1 bg-red-200 rounded">Delete</button>
                </div>

                {pausingTaskId === t.id && (
                  <form onSubmit={handlePause} className="space-y-2">
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
              </>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
