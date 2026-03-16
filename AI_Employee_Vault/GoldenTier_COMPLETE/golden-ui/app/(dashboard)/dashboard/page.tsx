export default function DashboardPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
      <p className="text-gray-600 dark:text-gray-400">Redirecting to main dashboard...</p>
      <script dangerouslySetInnerHTML={{
        __html: 'window.location.href = "/";'
      }} />
    </div>
  );
}