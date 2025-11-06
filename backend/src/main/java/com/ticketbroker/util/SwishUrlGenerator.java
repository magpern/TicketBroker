package com.ticketbroker.util;

import org.springframework.stereotype.Component;

@Component
public class SwishUrlGenerator {
    public String generateSwishUrl(String phone, Integer amount, String bookingRef) {
        String cleanPhone = phone.replace(" ", "").replace("-", "");
        return String.format("https://app.swish.nu/1/p/sw/?sw=%s&amt=%d&cur=SEK&msg=%s&src=qr", 
                cleanPhone, amount, bookingRef);
    }
}

