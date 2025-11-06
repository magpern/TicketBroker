import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../services/api'
import { BookingResponse } from '../types/booking'
import './BookingSuccessPage.css'

function BookingSuccessPage() {
  const { reference, email } = useParams<{ reference: string; email: string }>()
  const [booking, setBooking] = useState<BookingResponse | null>(null)
  const [swishUrl, setSwishUrl] = useState<string>('')

  useEffect(() => {
    if (reference && email) {
      api.get(`/public/bookings/${reference}?email=${email}`).then((response) => {
        setBooking(response.data)
      })
    }
  }, [reference, email])

  const handleInitiatePayment = async () => {
    if (reference && email) {
      try {
        const response = await api.post(`/public/bookings/${reference}/initiate-payment?email=${email}`)
        setSwishUrl(response.data.swishUrl)
        window.open(response.data.swishUrl, '_blank')
      } catch (error) {
        console.error('Failed to initiate payment:', error)
      }
    }
  }

  if (!booking) {
    return <div>Loading...</div>
  }

  return (
    <div className="booking-success-page">
      <h1>Bokning bekräftad!</h1>
      <div className="booking-details">
        <p><strong>Bokningsreferens:</strong> {booking.bookingReference}</p>
        <p><strong>Namn:</strong> {booking.firstName} {booking.lastName}</p>
        <p><strong>Totalt att betala:</strong> {booking.totalAmount} kr</p>
        
        {!swishUrl && (
          <button onClick={handleInitiatePayment} className="btn btn-primary">
            Betala nu med Swish
          </button>
        )}
      </div>
    </div>
  )
}

export default BookingSuccessPage

