import { useState } from 'react'
import { Save, RefreshCw } from 'lucide-react'

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    // Credit Settings
    signupBonus: 2500,
    adWatchReward: 100,
    maxAdsPerDay: 5,
    referralBonus: 500,
    defaultCreationCost: 100,
    
    // Feature Toggles
    battlesEnabled: true,
    maintenanceMode: false,
    newUserRegistration: true,
    publicCreationSharing: true,
    
    // Content Settings
    maxFileSize: 10, // MB
    allowedFormats: ['jpg', 'jpeg', 'png', 'webp'],
    autoModerationEnabled: true,
    moderationThreshold: 0.8,
    
    // Notification Settings
    emailNotifications: true,
    pushNotifications: true,
    adminAlerts: true,
    alertThreshold: 100,
  })

  const handleSave = () => {
    console.log('Saving settings:', settings)
    // Implementation will be added
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">System Settings</h1>
          <p className="text-gray-600">Configure platform settings and preferences</p>
        </div>
        <button onClick={handleSave} className="btn-primary">
          <Save className="h-4 w-4 mr-2" />
          Save Changes
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Credit Settings */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Credit Settings</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Signup Bonus Credits
              </label>
              <input
                type="number"
                value={settings.signupBonus}
                onChange={(e) => setSettings(prev => ({ ...prev, signupBonus: Number(e.target.value) }))}
                className="input"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ad Watch Reward
              </label>
              <input
                type="number"
                value={settings.adWatchReward}
                onChange={(e) => setSettings(prev => ({ ...prev, adWatchReward: Number(e.target.value) }))}
                className="input"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Ads Per Day
              </label>
              <input
                type="number"
                value={settings.maxAdsPerDay}
                onChange={(e) => setSettings(prev => ({ ...prev, maxAdsPerDay: Number(e.target.value) }))}
                className="input"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Referral Bonus
              </label>
              <input
                type="number"
                value={settings.referralBonus}
                onChange={(e) => setSettings(prev => ({ ...prev, referralBonus: Number(e.target.value) }))}
                className="input"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Default Creation Cost
              </label>
              <input
                type="number"
                value={settings.defaultCreationCost}
                onChange={(e) => setSettings(prev => ({ ...prev, defaultCreationCost: Number(e.target.value) }))}
                className="input"
              />
            </div>
          </div>
        </div>

        {/* Feature Toggles */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Feature Toggles</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-900">Battles Feature</label>
                <p className="text-sm text-gray-500">Enable battle competitions</p>
              </div>
              <input
                type="checkbox"
                checked={settings.battlesEnabled}
                onChange={(e) => setSettings(prev => ({ ...prev, battlesEnabled: e.target.checked }))}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-900">Maintenance Mode</label>
                <p className="text-sm text-gray-500">Put the platform in maintenance mode</p>
              </div>
              <input
                type="checkbox"
                checked={settings.maintenanceMode}
                onChange={(e) => setSettings(prev => ({ ...prev, maintenanceMode: e.target.checked }))}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-900">New User Registration</label>
                <p className="text-sm text-gray-500">Allow new users to register</p>
              </div>
              <input
                type="checkbox"
                checked={settings.newUserRegistration}
                onChange={(e) => setSettings(prev => ({ ...prev, newUserRegistration: e.target.checked }))}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-900">Public Creation Sharing</label>
                <p className="text-sm text-gray-500">Allow users to share creations publicly</p>
              </div>
              <input
                type="checkbox"
                checked={settings.publicCreationSharing}
                onChange={(e) => setSettings(prev => ({ ...prev, publicCreationSharing: e.target.checked }))}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
            </div>
          </div>
        </div>

        {/* Content Settings */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Content Settings</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max File Upload Size (MB)
              </label>
              <input
                type="number"
                value={settings.maxFileSize}
                onChange={(e) => setSettings(prev => ({ ...prev, maxFileSize: Number(e.target.value) }))}
                className="input"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Allowed Image Formats
              </label>
              <input
                type="text"
                value={settings.allowedFormats.join(', ')}
                onChange={(e) => setSettings(prev => ({ 
                  ...prev, 
                  allowedFormats: e.target.value.split(', ').map(f => f.trim()) 
                }))}
                className="input"
                placeholder="jpg, jpeg, png, webp"
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-900">Auto Moderation</label>
                <p className="text-sm text-gray-500">Enable automatic content moderation</p>
              </div>
              <input
                type="checkbox"
                checked={settings.autoModerationEnabled}
                onChange={(e) => setSettings(prev => ({ ...prev, autoModerationEnabled: e.target.checked }))}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Moderation Threshold (0-1)
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={settings.moderationThreshold}
                onChange={(e) => setSettings(prev => ({ ...prev, moderationThreshold: Number(e.target.value) }))}
                className="input"
              />
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Notification Settings</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-900">Email Notifications</label>
                <p className="text-sm text-gray-500">Send email notifications to users</p>
              </div>
              <input
                type="checkbox"
                checked={settings.emailNotifications}
                onChange={(e) => setSettings(prev => ({ ...prev, emailNotifications: e.target.checked }))}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-900">Push Notifications</label>
                <p className="text-sm text-gray-500">Send push notifications to mobile apps</p>
              </div>
              <input
                type="checkbox"
                checked={settings.pushNotifications}
                onChange={(e) => setSettings(prev => ({ ...prev, pushNotifications: e.target.checked }))}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-900">Admin Alerts</label>
                <p className="text-sm text-gray-500">Send alerts to administrators</p>
              </div>
              <input
                type="checkbox"
                checked={settings.adminAlerts}
                onChange={(e) => setSettings(prev => ({ ...prev, adminAlerts: e.target.checked }))}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Alert Threshold
              </label>
              <input
                type="number"
                value={settings.alertThreshold}
                onChange={(e) => setSettings(prev => ({ ...prev, alertThreshold: Number(e.target.value) }))}
                className="input"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}