// TaskCard.jsx
export default function TaskCard({ task, onAction }) {
    return (
      <div
        className="
          flex flex-col justify-between
          bg-surface
          border-l-4 border-primary-light dark:border-accent-light
          hover:ring-2 hover:ring-primary-dark
          rounded-2xl p-4
        "
      >
        <div>
          <h3 className="text-xl font-semibold text-white">{task.title}</h3>
          <p className="text-gray-300">{task.description}</p>
        </div>
        <footer className="flex items-center justify-between mt-4">
          <span className="text-sm text-gray-400">
            {task.dueDateFormatted}
          </span>
          <div className="space-x-2">
            <button className="px-2 py-1 bg-primary text-black rounded hover:bg-primary-dark dark:hover:bg-primary">
              Start
            </button>
            <button className="px-2 py-1 bg-accent text-black rounded hover:bg-accent-dark dark:hover:bg-accent">
              Pause
            </button>
            {/* …other actions… */}
          </div>
        </footer>
      </div>
    );
  }
