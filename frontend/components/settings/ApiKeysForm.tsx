'use client'

import { useState, useEffect } from 'react'
import { useSettingsStore } from '@/lib/store'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Eye, EyeOff } from 'lucide-react'
import { toast } from 'sonner'

export default function ApiKeysForm() {
  const [googleKey, setGoogleKey] = useState('')
  const [sarvamKey, setSarvamKey] = useState('')
  const [showGoogleKey, setShowGoogleKey] = useState(false)
  const [showSarvamKey, setShowSarvamKey] = useState(false)
  const [isSaved, setIsSaved] = useState(false)

  const { googleApiKey, sarvamApiKey, setGoogleApiKey, setSarvamApiKey, saveToLocalStorage } = useSettingsStore()

  useEffect(() => {
    setGoogleKey(googleApiKey)
    setSarvamKey(sarvamApiKey)
  }, [googleApiKey, sarvamApiKey])

  const handleSave = () => {
    if (!googleKey.trim()) {
      toast.error('Google API key is required')
      return
    }
    if (!sarvamKey.trim()) {
      toast.error('Sarvam API key is required')
      return
    }

    setGoogleApiKey(googleKey)
    setSarvamApiKey(sarvamKey)
    saveToLocalStorage()
    setIsSaved(true)
    toast.success('API keys saved successfully')
    
    setTimeout(() => setIsSaved(false), 3000)
  }

  return (
    <div className="space-y-6">
      {/* Google API Key */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-foreground">
          Google API Key
        </label>
        <p className="text-xs text-muted-foreground">
          Used for processing loan queries and recommendations
        </p>
        <div className="flex gap-2">
          <Input
            type={showGoogleKey ? 'text' : 'password'}
            value={googleKey}
            onChange={(e) => setGoogleKey(e.target.value)}
            placeholder="sk-..."
            className="flex-1"
          />
          <Button
            type="button"
            size="icon"
            variant="outline"
            onClick={() => setShowGoogleKey(!showGoogleKey)}
            className="h-10 w-10"
          >
            {showGoogleKey ? (
              <EyeOff className="w-4 h-4" />
            ) : (
              <Eye className="w-4 h-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Sarvam API Key */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-foreground">
          Sarvam API Key
        </label>
        <p className="text-xs text-muted-foreground">
          Used for voice transcription and text-to-speech
        </p>
        <div className="flex gap-2">
          <Input
            type={showSarvamKey ? 'text' : 'password'}
            value={sarvamKey}
            onChange={(e) => setSarvamKey(e.target.value)}
            placeholder="sa-..."
            className="flex-1"
          />
          <Button
            type="button"
            size="icon"
            variant="outline"
            onClick={() => setShowSarvamKey(!showSarvamKey)}
            className="h-10 w-10"
          >
            {showSarvamKey ? (
              <EyeOff className="w-4 h-4" />
            ) : (
              <Eye className="w-4 h-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Save Button */}
      <div className="pt-4">
        <Button
          onClick={handleSave}
          className="w-full sm:w-auto"
          variant={isSaved ? 'outline' : 'default'}
        >
          {isSaved ? 'Saved!' : 'Save API Keys'}
        </Button>
        <p className="text-xs text-muted-foreground mt-2">
          Your keys are stored locally in your browser and never sent to our servers.
        </p>
      </div>
    </div>
  )
}
