import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import { BookingRequest } from '../types/booking'
import './BookingPage.css'

function BookingPage() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState<BookingRequest>({
    showId: 0,
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    adultTickets: 0,
    studentTickets: 0,
    gdprConsent: false,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await api.post('/public/bookings', formData)
      navigate(`/booking/success/${response.data.bookingReference}/${response.data.email}`)
    } catch (error) {
      console.error('Booking failed:', error)
      alert('Bokningen misslyckades. Försök igen.')
    }
  }

  return (
    <div className="booking-page">
      <h1>Boka biljetter</h1>
      <form onSubmit={handleSubmit} className="booking-form">
        <div className="form-group">
          <label>Förnamn</label>
          <input
            type="text"
            required
            value={formData.firstName}
            onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
          />
        </div>
        
        <div className="form-group">
          <label>Efternamn</label>
          <input
            type="text"
            required
            value={formData.lastName}
            onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
          />
        </div>
        
        <div className="form-group">
          <label>E-post</label>
          <input
            type="email"
            required
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
        </div>
        
        <div className="form-group">
          <label>Telefon</label>
          <input
            type="tel"
            required
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
          />
        </div>
        
        <div className="form-group">
          <label>Ordinariebiljetter</label>
          <input
            type="number"
            min="0"
            value={formData.adultTickets}
            onChange={(e) => setFormData({ ...formData, adultTickets: parseInt(e.target.value) || 0 })}
          />
        </div>
        
        <div className="form-group">
          <label>Studentbiljetter</label>
          <input
            type="number"
            min="0"
            value={formData.studentTickets}
            onChange={(e) => setFormData({ ...formData, studentTickets: parseInt(e.target.value) || 0 })}
          />
        </div>
        
        <div className="form-group">
          <label>
            <input
              type="checkbox"
              required
              checked={formData.gdprConsent}
              onChange={(e) => setFormData({ ...formData, gdprConsent: e.target.checked })}
            />
            Jag godkänner behandling av personuppgifter
          </label>
        </div>
        
        <button type="submit" className="btn btn-primary">
          Boka
        </button>
      </form>
    </div>
  )
}

export default BookingPage

