import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { Show } from '../types/booking'
import './HomePage.css'

function HomePage() {
  const [shows, setShows] = useState<Show[]>([])
  const [settings, setSettings] = useState<any>({})

  useEffect(() => {
    api.get('/public/shows').then((response) => {
      setShows(response.data)
    })
    api.get('/public/settings').then((response) => {
      setSettings(response.data)
    })
  }, [])

  return (
    <div className="home-page">
      <header className="header">
        <h1>{settings.concertName || 'Klasskonsert 24C'}</h1>
      </header>
      
      <main className="main-content">
        <div className="concert-info">
          <h2>Konsertinformation</h2>
          <p><strong>Datum:</strong> {settings.concertDate}</p>
          <p><strong>Plats:</strong> {settings.concertVenue}</p>
          
          <div className="pricing">
            <h3>Priser</h3>
            <p><strong>Ordinariebiljett:</strong> {settings.adultPrice} kr</p>
            <p><strong>Studentbiljett:</strong> {settings.studentPrice} kr</p>
          </div>
        </div>

        <div className="shows-list">
          <h2>Tillgängliga tider</h2>
          {shows.map((show) => (
            <div key={show.id} className="show-card">
              <p><strong>Tid:</strong> {show.startTime} - {show.endTime}</p>
              <p><strong>Tillgängliga biljetter:</strong> {show.availableTickets}</p>
            </div>
          ))}
        </div>

        <div className="cta">
          <Link to="/booking" className="btn btn-primary">
            Boka biljetter nu
          </Link>
        </div>
      </main>
    </div>
  )
}

export default HomePage

