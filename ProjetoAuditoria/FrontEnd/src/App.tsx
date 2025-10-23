import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useEffect } from 'react';
import { Layout } from './components/Layout';
import { 
  Dashboard, 
  NewAudit, 
  AuditProgress, 
  Results, 
  History, 
  Reports, 
  Settings, 
  Documentation, 
  AdminPanel, 
  Monitoring, 
  Metrics,
  PrometheusMetrics
} from './pages';
import { ProcessItem } from './pages/ProcessItem';
import { ErrorPage } from './pages/ErrorPage';
import { useThemeStore } from './store/themeStore';
import { NotificationCenter } from './components/NotificationCenter';
import { TestNewEndpoints } from './components/TestNewEndpoints';

function App() {
  const { theme } = useThemeStore();

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  return (
    <Router>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Layout>
          <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/audit/new" element={<NewAudit />} />
          <Route path="/audit/active" element={<AuditProgress />} />
          <Route path="/audit/progress/:id" element={<AuditProgress />} />
          <Route path="/audit/result/:id" element={<Results />} />
          <Route path="/audit/history" element={<History />} />
          <Route path="/audit/documentation/:auditId" element={<Documentation />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/metrics" element={<Metrics />} />
          <Route path="/admin" element={<AdminPanel />} />
          <Route path="/monitoring" element={<Monitoring />} />
          <Route path="/metrics" element={<Metrics />} />
          <Route path="/prometheus" element={<PrometheusMetrics />} />
          <Route path="/test-endpoints" element={<TestNewEndpoints />} />
          <Route path="/process-item" element={<ProcessItem />} />
          <Route path="/error" element={<ErrorPage />} />
        </Routes>
        </Layout>
        <NotificationCenter />
      </div>
    </Router>
  );
}

export default App;
