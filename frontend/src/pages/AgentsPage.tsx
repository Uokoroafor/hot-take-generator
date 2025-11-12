import { useState, useEffect } from 'react';
import config from '../config';
import './Pages.css';

interface Agent {
  name: string;
  description: string;
  model: string;
  avgResponseTime?: number;
  lastUsed?: string;
}

const AgentsPage = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [defaultAgent, setDefaultAgent] = useState<string>('');
  const [testingAgent, setTestingAgent] = useState<string | null>(null);

  useEffect(() => {
    fetchAgents();
    loadDefaultAgent();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch(`${config.apiBaseUrl}/api/agents`);
      if (response.ok) {
        const data = await response.json();
        setAgents(data.agents || []);
      }
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadDefaultAgent = () => {
    const saved = localStorage.getItem('defaultAgent');
    if (saved) {
      setDefaultAgent(saved);
    }
  };

  const setAsDefault = (agentName: string) => {
    setDefaultAgent(agentName);
    localStorage.setItem('defaultAgent', agentName);
  };

  const testAgent = async (agentName: string) => {
    setTestingAgent(agentName);
    const startTime = Date.now();
    
    try {
      const response = await fetch(`${config.apiBaseUrl}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: 'test',
          style: 'controversial',
          agent_type: agentName,
        }),
      });
      
      const endTime = Date.now();
      const responseTime = endTime - startTime;
      
      if (response.ok) {
        // Update agent with response time
        setAgents(prev => prev.map(a => 
          a.name === agentName 
            ? { ...a, avgResponseTime: responseTime, lastUsed: new Date().toISOString() }
            : a
        ));
      }
    } catch (error) {
      console.error('Failed to test agent:', error);
    } finally {
      setTestingAgent(null);
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1>🤖 AI Agents</h1>
          <p>Loading agents...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>🤖 AI Agents</h1>
        <p>Manage and test your AI agents</p>
      </div>

      <div className="info-box">
        <p>
          <strong>Default Agent:</strong> {defaultAgent || 'None selected'}
        </p>
        <p className="help-text">
          The default agent will be used for generating hot takes. You can override this per-request.
        </p>
      </div>

      {agents.length === 0 ? (
        <div className="empty-state">
          <p>No agents available. Check your API configuration.</p>
        </div>
      ) : (
        <div className="agents-grid">
          {agents.map(agent => (
            <div key={agent.name} className="agent-card">
              <div className="agent-header">
                <h3>{agent.name}</h3>
                {defaultAgent === agent.name && (
                  <span className="badge badge-success">Default</span>
                )}
              </div>
              
              <p className="agent-description">{agent.description}</p>
              
              <div className="agent-details">
                <div className="detail-item">
                  <span className="detail-label">Model:</span>
                  <span className="detail-value">{agent.model}</span>
                </div>
                
                {agent.avgResponseTime && (
                  <div className="detail-item">
                    <span className="detail-label">Avg Response:</span>
                    <span className="detail-value">{agent.avgResponseTime}ms</span>
                  </div>
                )}
                
                {agent.lastUsed && (
                  <div className="detail-item">
                    <span className="detail-label">Last Used:</span>
                    <span className="detail-value">
                      {new Date(agent.lastUsed).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>

              <div className="agent-actions">
                {defaultAgent !== agent.name && (
                  <button
                    onClick={() => setAsDefault(agent.name)}
                    className="btn-primary"
                  >
                    Set as Default
                  </button>
                )}
                <button
                  onClick={() => testAgent(agent.name)}
                  className="btn-secondary"
                  disabled={testingAgent === agent.name}
                >
                  {testingAgent === agent.name ? 'Testing...' : '⚡ Test Speed'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AgentsPage;
