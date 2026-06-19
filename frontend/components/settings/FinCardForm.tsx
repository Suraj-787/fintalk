'use client'

import { useState, useEffect } from 'react'
import { useSettingsStore, FinCard } from '@/lib/store'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { toast } from 'sonner'

// Must match Python backend config.py EMPLOYMENT_TYPES
const EMPLOYMENT_TYPES = ['Salaried', 'Self-Employed', 'Freelancer', 'Unemployed'] as const

const defaultForm: FinCard = {
  fullName: '',
  age: 18,
  occupation: '',
  employmentType: 'Salaried',
  location: '',
  monthlyIncome: 0,
  creditScore: 300,
  monthlyExpenses: 0,
  monthlyEmi: 0,
  amountOutstanding: 0,
  creditCardDues: 0,
}

export default function FinCardForm() {
  const [formData, setFormData] = useState<FinCard>(defaultForm)
  const [isSaved, setIsSaved] = useState(false)

  const { finCard, setFinCard } = useSettingsStore()

  useEffect(() => {
    setFormData(finCard)
  }, [finCard])

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target
    const numericFields = [
      'age', 'monthlyIncome', 'creditScore', 'monthlyExpenses',
      'monthlyEmi', 'amountOutstanding', 'creditCardDues',
    ]
    setFormData((prev) => ({
      ...prev,
      [name]: numericFields.includes(name) ? parseFloat(value) || 0 : value,
    }))
  }

  const handleSave = () => {
    if (!formData.fullName.trim()) {
      toast.error('Full name is required')
      return
    }
    if (formData.age < 18 || formData.age > 100) {
      toast.error('Age must be between 18 and 100')
      return
    }
    if (formData.creditScore < 300 || formData.creditScore > 900) {
      toast.error('Credit score must be between 300 and 900')
      return
    }

    setFinCard(formData)
    setIsSaved(true)
    toast.success('FinCard saved successfully!')
    setTimeout(() => setIsSaved(false), 3000)
  }

  const getCreditScoreColor = (score: number) => {
    if (score < 580) return 'text-red-500'
    if (score < 670) return 'text-orange-500'
    if (score < 740) return 'text-yellow-500'
    return 'text-green-500'
  }

  const getCreditScoreLabel = (score: number) => {
    if (score < 580) return 'Poor'
    if (score < 670) return 'Fair'
    if (score < 740) return 'Good'
    return 'Excellent'
  }

  const inputClass = 'w-full px-3 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary'

  return (
    <div className="space-y-6">
      {/* Personal Information */}
      <div>
        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">
          Personal Information
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Full Name */}
          <div className="space-y-1">
            <label className="text-sm font-medium text-foreground">Full Name</label>
            <Input
              type="text"
              name="fullName"
              value={formData.fullName}
              onChange={handleChange}
              placeholder="Ravi Kumar"
            />
          </div>

          {/* Age */}
          <div className="space-y-1">
            <label className="text-sm font-medium text-foreground">Age</label>
            <Input
              type="number"
              name="age"
              value={formData.age || ''}
              onChange={handleChange}
              placeholder="28"
              min="18"
              max="100"
            />
          </div>

          {/* Occupation */}
          <div className="space-y-1">
            <label className="text-sm font-medium text-foreground">Occupation</label>
            <Input
              type="text"
              name="occupation"
              value={formData.occupation}
              onChange={handleChange}
              placeholder="Software Engineer"
            />
          </div>

          {/* Employment Type */}
          <div className="space-y-1">
            <label className="text-sm font-medium text-foreground">Employment Type</label>
            <select
              name="employmentType"
              value={formData.employmentType}
              onChange={handleChange}
              className={inputClass}
            >
              {EMPLOYMENT_TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>

          {/* Location */}
          <div className="space-y-1 sm:col-span-2">
            <label className="text-sm font-medium text-foreground">Location</label>
            <Input
              type="text"
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder="Mumbai, Maharashtra"
            />
          </div>
        </div>
      </div>

      {/* Financial Information */}
      <div>
        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">
          Financial Information
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Monthly Income */}
          <div className="space-y-1">
            <label className="text-sm font-medium text-foreground">Monthly Income (₹)</label>
            <Input
              type="number"
              name="monthlyIncome"
              value={formData.monthlyIncome || ''}
              onChange={handleChange}
              placeholder="50000"
              min="0"
            />
          </div>

          {/* Credit Score */}
          <div className="space-y-1">
            <label className="text-sm font-medium text-foreground">Credit Score (300–900)</label>
            <div className="flex gap-2">
              <Input
                type="number"
                name="creditScore"
                value={formData.creditScore || ''}
                onChange={handleChange}
                placeholder="750"
                min="300"
                max="900"
                className="flex-1"
              />
              {formData.creditScore >= 300 && (
                <div className="flex items-center px-3 py-2 bg-muted rounded-md whitespace-nowrap">
                  <span className={`text-sm font-medium ${getCreditScoreColor(formData.creditScore)}`}>
                    {getCreditScoreLabel(formData.creditScore)}
                  </span>
                </div>
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              300–579: Poor · 580–669: Fair · 670–739: Good · 740–900: Excellent
            </p>
          </div>

          {/* Monthly Expenses */}
          <div className="space-y-1">
            <label className="text-sm font-medium text-foreground">Monthly Expenses (₹)</label>
            <Input
              type="number"
              name="monthlyExpenses"
              value={formData.monthlyExpenses || ''}
              onChange={handleChange}
              placeholder="20000"
              min="0"
            />
          </div>

          {/* Monthly EMI */}
          <div className="space-y-1">
            <label className="text-sm font-medium text-foreground">Monthly EMI (₹)</label>
            <Input
              type="number"
              name="monthlyEmi"
              value={formData.monthlyEmi || ''}
              onChange={handleChange}
              placeholder="5000"
              min="0"
            />
          </div>
        </div>
      </div>

      {/* Debt Information */}
      <div>
        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">
          Outstanding Debt
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Amount Outstanding */}
          <div className="space-y-1">
            <label className="text-sm font-medium text-foreground">Amount Outstanding (₹)</label>
            <Input
              type="number"
              name="amountOutstanding"
              value={formData.amountOutstanding || ''}
              onChange={handleChange}
              placeholder="100000"
              min="0"
            />
          </div>

          {/* Credit Card Dues */}
          <div className="space-y-1">
            <label className="text-sm font-medium text-foreground">Credit Card Dues (₹)</label>
            <Input
              type="number"
              name="creditCardDues"
              value={formData.creditCardDues || ''}
              onChange={handleChange}
              placeholder="15000"
              min="0"
            />
          </div>
        </div>
      </div>

      {/* Save */}
      <div className="pt-4 border-t border-border">
        <Button
          onClick={handleSave}
          className="w-full sm:w-auto"
          variant={isSaved ? 'outline' : 'default'}
        >
          {isSaved ? '✅ Saved!' : 'Save FinCard'}
        </Button>
      </div>
    </div>
  )
}
