package com.ticketbroker.util;

import org.springframework.stereotype.Component;

@Component
public class TicketReferenceGenerator {
    public String generateTicketReference(String bookingRef, String ticketType, Integer ticketNumber) {
        String prefix = "normal".equals(ticketType) ? "N" : "D";
        return String.format("%s-%s%02d", bookingRef, prefix, ticketNumber);
    }
}

