import { useState } from 'react';
import { useLocalStorage } from '../hooks/useLocalStorage';
import { TIME_RANGES, REFRESH_INTERVALS } from '../utils/constants';
import { Settings as SettingsIcon, Bell, Palette, Database, Shield } from 'lucide-react';

interface SettingsData {
  dashboard: {
    refreshInterval: number;
    defaultTimeRange: string;
    enableRealTime: boolean;
    theme: 'light' | 'dark' | 'auto';
  };
  alerts: {
    enabled: boolean;
    email: boolean;
    push: boolean;
    sentimentThreshold: number;
    issueAlerts: string[];
  };
  data: {
    cacheEnabled: boolean;
    offlineMode: boolean;
    dataRetention: number;
  };
  privacy: {
    analytics: boolean;
    tracking: boolean;
    datasharing: boolean;
  };
}

const defaultSettings: SettingsData = {
  dashboard: {
    refreshInterval: REFRESH_INTERVALS.NORMAL,
    defaultTimeRange: '30d',
    enableRealTime: true,
    theme: 'light'
  },
  alerts: {
    enabled: true,
    email: true,
    push: false,
    sentimentThreshold: 0.3,
    issueAlerts: ['Jobs', 'Health']
  },
  data: {
    cacheEnabled: true,
    offlineMode: false,
    dataRetention: 90
  },
  privacy: {
    analytics: true,
    tracking: false,
    datasharing: false
  }
};

export default function Settings() {
  const [settings, setSettings] = useLocalStorage<SettingsData>('dashboard-settings', defaultSettings);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsSaving(false);
  };

  const updateSetting = (section: keyof SettingsData, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }));
  };

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: SettingsIcon },
    { id: 'alerts', label: 'Alerts', icon: Bell },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'data', label: 'Data', icon: Database },
    { id: 'privacy', label: 'Privacy', icon: Shield }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600">Customize your dashboard experience</p>
        </div>
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {isSaving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <nav className="space-y-1">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-50 text-blue-700 border-l-4 border-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <tab.icon className="w-5 h-5 mr-3" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            {activeTab === 'dashboard' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900">Dashboard Settings</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Refresh Interval
                    </label>
                    <select
                      value={settings.dashboard.refreshInterval}
                      onChange={(e) => updateSetting('dashboard', 'refreshInterval', Number(e.target.value))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    >
                      <option value={REFRESH_INTERVALS.REAL_TIME}>30 seconds</option>
                      <option value={REFRESH_INTERVALS.FREQUENT}>1 minute</option>
                      <option value={REFRESH_INTERVALS.NORMAL}>5 minutes</option>
                      <option value={REFRESH_INTERVALS.SLOW}>10 minutes</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Default Time Range
                    </label>
                    <select
                      value={settings.dashboard.defaultTimeRange}
                      onChange={(e) => updateSetting('dashboard', 'defaultTimeRange', e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    >
                      {Object.entries(TIME_RANGES).map(([key, range]) => (
                        <option key={key} value={key}>{range.label}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Real-time Updates</h4>
                    <p className="text-sm text-gray-500">Enable automatic data refresh</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.dashboard.enableRealTime}
                    onChange={(e) => updateSetting('dashboard', 'enableRealTime', e.target.checked)}
                    className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                  />
                </div>
              </div>
            )}

            {activeTab === 'alerts' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900">Alert Settings</h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">Enable Alerts</h4>
                      <p className="text-sm text-gray-500">Receive notifications for important changes</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.alerts.enabled}
                      onChange={(e) => updateSetting('alerts', 'enabled', e.target.checked)}
                      className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">Email Notifications</h4>
                      <p className="text-sm text-gray-500">Receive alerts via email</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.alerts.email}
                      onChange={(e) => updateSetting('alerts', 'email', e.target.checked)}
                      className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Sentiment Threshold ({settings.alerts.sentimentThreshold})
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={settings.alerts.sentimentThreshold}
                      onChange={(e) => updateSetting('alerts', 'sentimentThreshold', Number(e.target.value))}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Very Negative</span>
                      <span>Neutral</span>
                      <span>Very Positive</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'appearance' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900">Appearance</h3>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Theme
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {['light', 'dark', 'auto'].map(theme => (
                      <button
                        key={theme}
                        onClick={() => updateSetting('dashboard', 'theme', theme)}
                        className={`p-3 border rounded-lg text-sm font-medium capitalize transition-colors ${
                          settings.dashboard.theme === theme
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-300 hover:border-gray-400'
                        }`}
                      >
                        {theme}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'data' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900">Data Management</h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">Enable Caching</h4>
                      <p className="text-sm text-gray-500">Cache data for faster loading</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.data.cacheEnabled}
                      onChange={(e) => updateSetting('data', 'cacheEnabled', e.target.checked)}
                      className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Data Retention (days)
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="365"
                      value={settings.data.dataRetention}
                      onChange={(e) => updateSetting('data', 'dataRetention', Number(e.target.value))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'privacy' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900">Privacy Settings</h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">Analytics</h4>
                      <p className="text-sm text-gray-500">Help improve the app by sharing usage data</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.privacy.analytics}
                      onChange={(e) => updateSetting('privacy', 'analytics', e.target.checked)}
                      className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">Data Sharing</h4>
                      <p className="text-sm text-gray-500">Share anonymized data for research</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.privacy.datasharing}
                      onChange={(e) => updateSetting('privacy', 'datasharing', e.target.checked)}
                      className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}