export interface Show {
  id: number
  date: string
  startTime: string
  endTime: string
  totalTickets: number
  availableTickets: number
  createdAt: string
}

export interface BookingRequest {
  showId: number
  firstName: string
  lastName: string
  email: string
  phone: string
  adultTickets: number
  studentTickets: number
  gdprConsent: boolean
}

export interface BookingResponse {
  id: number
  bookingReference: string
  firstName: string
  lastName: string
  email: string
  phone: string
  adultTickets: number
  studentTickets: number
  totalAmount: number
  status: string
  buyerConfirmedPayment: boolean
  swishPaymentInitiated: boolean
  swishPaymentInitiatedAt: string | null
  createdAt: string
  confirmedAt: string | null
  show: Show
}

