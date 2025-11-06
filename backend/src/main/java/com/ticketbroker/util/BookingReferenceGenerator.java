package com.ticketbroker.util;

import com.ticketbroker.repository.BookingRepository;
import org.springframework.stereotype.Component;

import java.util.Random;

@Component
public class BookingReferenceGenerator {
    private static final String CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    private static final int REFERENCE_LENGTH = 5;
    private final Random random = new Random();
    private final BookingRepository bookingRepository;
    
    public BookingReferenceGenerator(BookingRepository bookingRepository) {
        this.bookingRepository = bookingRepository;
    }
    
    public String generateUniqueReference() {
        String reference;
        do {
            reference = generateReference();
        } while (bookingRepository.findByBookingReference(reference).isPresent());
        return reference;
    }
    
    private String generateReference() {
        StringBuilder sb = new StringBuilder(REFERENCE_LENGTH);
        for (int i = 0; i < REFERENCE_LENGTH; i++) {
            sb.append(CHARACTERS.charAt(random.nextInt(CHARACTERS.length())));
        }
        return sb.toString();
    }
}

