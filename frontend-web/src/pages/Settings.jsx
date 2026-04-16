import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Moon, Sun, Bell, Shield, Sliders, Cpu, Save } from 'lucide-react';

export default function Settings() {
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');
  const [notifications, setNotifications] = useState(localStorage.getItem('notifications') === 'true');
  const [llmTemp, setLlmTemp] = useState(parseFloat(localStorage.getItem('llmTemp')) || 0.2);
  const [agentStrictness, setAgentStrictness] = useState(localStorage.getItem('agentStrictness') || 'high');

  useEffect(() => {
    // Apply theme globally
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const handleSave = () => {
    localStorage.setItem('theme', theme);
    localStorage.setItem('notifications', notifications.toString());
    localStorage.setItem('llmTemp', llmTemp.toString());
    localStorage.setItem('agentStrictness', agentStrictness);
    
    // Simulate api update sync
    setTimeout(() => {
      alert("Settings have been fully saved and synchronized with System State.");
    }, 300);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-up relative z-10">
      <div className="flex items-center gap-4 mb-10">
        <div className="h-16 w-16 rounded-2xl bg-brand-500/10 flex items-center justify-center border border-brand-500/20 shadow-neon">
          <SettingsIcon className="h-8 w-8 text-brand-400" />
        </div>
        <div>
          <h1 className="text-4xl font-bold text-white tracking-tight">System Configuration</h1>
          <p className="text-slate-400 mt-2 text-lg">Manage application preferences and AI Agent boundaries.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Appearance Section */}
        <div className="bg-surface-2/60 backdrop-blur-glass border border-white/5 rounded-3xl p-8 hover:border-brand-500/30 transition-all duration-500 shadow-bento group">
          <div className="flex items-center gap-3 mb-6">
            <Moon className="w-6 h-6 text-brand-400" />
            <h2 className="text-2xl font-semibold text-white">Appearance</h2>
          </div>
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white font-medium">Dark Mode</p>
                <p className="text-sm text-slate-400">Toggle obsidian spatial theme</p>
              </div>
              <button 
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                className={`relative inline-flex h-7 w-14 items-center rounded-full transition-colors ${theme === 'dark' ? 'bg-brand-500 shadow-neon' : 'bg-slate-700'}`}
              >
                <span className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform ${theme === 'dark' ? 'translate-x-8' : 'translate-x-1'}`} />
              </button>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white font-medium">Push Notifications</p>
                <p className="text-sm text-slate-400">Alerts for diagnostic reports</p>
              </div>
              <button 
                onClick={() => setNotifications(!notifications)}
                className={`relative inline-flex h-7 w-14 items-center rounded-full transition-colors ${notifications ? 'bg-emerald-500 shadow-neon-emerald' : 'bg-slate-700'}`}
              >
                <span className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform ${notifications ? 'translate-x-8' : 'translate-x-1'}`} />
              </button>
            </div>
          </div>
        </div>

        {/* AI Agent Parameters */}
        <div className="bg-surface-2/60 backdrop-blur-glass border border-white/5 rounded-3xl p-8 hover:border-brand-500/30 transition-all duration-500 shadow-bento group">
          <div className="flex items-center gap-3 mb-6">
            <Cpu className="w-6 h-6 text-brand-400" />
            <h2 className="text-2xl font-semibold text-white">Agent Parameters</h2>
          </div>
          
          <div className="space-y-8">
            <div>
              <div className="flex justify-between mb-2">
                <p className="text-white font-medium">Diagnostic Temperature: <span className="text-brand-400">{llmTemp}</span></p>
              </div>
              <input 
                type="range" 
                min="0" max="1" step="0.1" 
                value={llmTemp}
                onChange={(e) => setLlmTemp(parseFloat(e.target.value))}
                className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-brand-500"
              />
              <p className="text-xs text-slate-500 mt-2">Lower matches rigid FDA protocols; Higher allows exploratory associations.</p>
            </div>

            <div>
              <p className="text-white font-medium mb-3">Self-Correction Strictness</p>
              <div className="grid grid-cols-3 gap-3">
                {['low', 'medium', 'high'].map((level) => (
                  <button
                    key={level}
                    onClick={() => setAgentStrictness(level)}
                    className={`py-2 px-4 rounded-xl border capitalize transition-all duration-300 ${agentStrictness === level ? 'bg-brand-500/20 border-brand-500 text-brand-400 shadow-neon' : 'border-white/10 text-slate-400 hover:border-white/30'}`}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

      </div>

      <div className="flex justify-end pt-6 border-t border-white/10">
        <button 
          onClick={handleSave}
          className="flex items-center justify-center gap-2 bg-brand-500/10 border border-brand-500/50 hover:bg-brand-500 text-white hover:text-obsidian hover:shadow-neon px-8 py-3 rounded-xl font-bold transition-all duration-300 transform hover:scale-105"
        >
          <Save className="w-5 h-5" />
          Apply Configuration
        </button>
      </div>

    </div>
  );
}
