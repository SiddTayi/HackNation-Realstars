import { useState } from 'react';
import { Login, UserPortal, AgentPortal, CaseDetail } from './pages';

function App() {
  const [user, setUser] = useState(null);
  const [currentView, setCurrentView] = useState('login');
  const [selectedCase, setSelectedCase] = useState(null);

  const handleLogin = (userData) => {
    setUser(userData);
    if (userData.role === 'user') {
      setCurrentView('userPortal');
    } else if (userData.role === 'agent') {
      setCurrentView('agentPortal');
    }
  };

  const handleLogout = () => {
    setUser(null);
    setCurrentView('login');
    setSelectedCase(null);
  };

  const handleSelectCase = (caseData) => {
    setSelectedCase(caseData);
    setCurrentView('caseDetail');
  };

  const handleBackToAgentPortal = () => {
    setSelectedCase(null);
    setCurrentView('agentPortal');
  };

  // Render based on current view
  if (currentView === 'login' || !user) {
    return <Login onLogin={handleLogin} />;
  }

  if (currentView === 'userPortal' && user.role === 'user') {
    return <UserPortal user={user} onLogout={handleLogout} />;
  }

  if (currentView === 'agentPortal' && user.role === 'agent') {
    return (
      <AgentPortal
        user={user}
        onLogout={handleLogout}
        onSelectCase={handleSelectCase}
      />
    );
  }

  if (currentView === 'caseDetail' && selectedCase) {
    return (
      <CaseDetail
        caseData={selectedCase}
        user={user}
        onLogout={handleLogout}
        onBack={handleBackToAgentPortal}
      />
    );
  }

  // Fallback to login
  return <Login onLogin={handleLogin} />;
}

export default App;
