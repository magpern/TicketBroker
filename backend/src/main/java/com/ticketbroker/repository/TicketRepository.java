package com.ticketbroker.repository;

import com.ticketbroker.model.Ticket;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface TicketRepository extends JpaRepository<Ticket, Long> {
    Optional<Ticket> findByTicketReference(String ticketReference);
    
    List<Ticket> findByBookingId(Long bookingId);
    
    List<Ticket> findByShowId(Long showId);
    
    List<Ticket> findByBuyerId(Long buyerId);
    
    List<Ticket> findByIsUsed(Boolean isUsed);
}

