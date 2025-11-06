package com.ticketbroker.controller.api;

import com.ticketbroker.dto.BookingResponse;
import com.ticketbroker.model.Booking;
import com.ticketbroker.model.Ticket;
import com.ticketbroker.repository.AuditLogRepository;
import com.ticketbroker.repository.BookingRepository;
import com.ticketbroker.repository.TicketRepository;
import com.ticketbroker.service.BookingService;
import com.ticketbroker.service.EmailService;
import com.ticketbroker.service.ExcelService;
import com.ticketbroker.service.PdfService;
import com.ticketbroker.service.SettingsService;
import com.ticketbroker.service.TicketService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/admin")
@CrossOrigin(origins = "*")
public class AdminApiController {
    private final BookingRepository bookingRepository;
    private final TicketRepository ticketRepository;
    private final AuditLogRepository auditLogRepository;
    private final BookingService bookingService;
    private final TicketService ticketService;
    private final EmailService emailService;
    private final PdfService pdfService;
    private final ExcelService excelService;
    private final SettingsService settingsService;
    
    public AdminApiController(BookingRepository bookingRepository, TicketRepository ticketRepository,
                            AuditLogRepository auditLogRepository, BookingService bookingService,
                            TicketService ticketService, EmailService emailService,
                            PdfService pdfService, ExcelService excelService,
                            SettingsService settingsService) {
        this.bookingRepository = bookingRepository;
        this.ticketRepository = ticketRepository;
        this.auditLogRepository = auditLogRepository;
        this.bookingService = bookingService;
        this.ticketService = ticketService;
        this.emailService = emailService;
        this.pdfService = pdfService;
        this.excelService = excelService;
        this.settingsService = settingsService;
    }
    
    @GetMapping("/bookings")
    public ResponseEntity<List<BookingResponse>> getAllBookings() {
        List<Booking> bookings = bookingRepository.findAll();
        List<BookingResponse> responses = bookings.stream()
                .map(BookingResponse::fromEntity)
                .collect(Collectors.toList());
        return ResponseEntity.ok(responses);
    }
    
    @PostMapping("/bookings/{id}/confirm-payment")
    public ResponseEntity<BookingResponse> confirmPayment(@PathVariable Long id,
                                                          @RequestParam(defaultValue = "admin") String adminUser) {
        Booking booking = bookingRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Booking not found"));
        
        Booking confirmed = bookingService.confirmPaymentByAdmin(booking, adminUser);
        
        // Send confirmation email with PDF
        try {
            byte[] pdfData = pdfService.generateTicketsPdf(confirmed);
            emailService.sendPaymentConfirmed(confirmed, pdfData);
        } catch (Exception e) {
            // Log error but don't fail
        }
        
        return ResponseEntity.ok(BookingResponse.fromEntity(confirmed));
    }
    
    @DeleteMapping("/bookings/{id}")
    public ResponseEntity<Void> deleteBooking(@PathVariable Long id) {
        bookingService.deleteBooking(id);
        return ResponseEntity.noContent().build();
    }
    
    @GetMapping("/tickets")
    public ResponseEntity<List<Map<String, Object>>> getAllTickets() {
        List<Ticket> tickets = ticketRepository.findAll();
        List<Map<String, Object>> responses = tickets.stream().map(ticket -> {
            Map<String, Object> map = new HashMap<>();
            map.put("id", ticket.getId());
            map.put("ticketReference", ticket.getTicketReference());
            map.put("ticketType", ticket.getTicketType());
            map.put("isUsed", ticket.getIsUsed());
            map.put("usedAt", ticket.getUsedAt());
            map.put("checkedBy", ticket.getCheckedBy());
            map.put("bookingReference", ticket.getBooking().getBookingReference());
            map.put("showTime", ticket.getShow().getStartTime() + "-" + ticket.getShow().getEndTime());
            return map;
        }).collect(Collectors.toList());
        return ResponseEntity.ok(responses);
    }
    
    @PostMapping("/tickets/{id}/toggle-state")
    public ResponseEntity<Map<String, Object>> toggleTicketState(@PathVariable Long id,
                                                                 @RequestParam String checkerUser) {
        Ticket ticket = ticketRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Ticket not found"));
        
        ticketService.toggleTicketState(ticket, checkerUser);
        
        Map<String, Object> response = new HashMap<>();
        response.put("id", ticket.getId());
        response.put("isUsed", ticket.getIsUsed());
        return ResponseEntity.ok(response);
    }
    
    @DeleteMapping("/tickets/{id}")
    public ResponseEntity<Void> deleteTicket(@PathVariable Long id,
                                             @RequestParam(defaultValue = "admin") String adminUser,
                                             @RequestParam(required = false) String reason) {
        Ticket ticket = ticketRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Ticket not found"));
        
        ticketService.deleteTicket(ticket, adminUser, reason);
        return ResponseEntity.noContent().build();
    }
    
    @GetMapping("/export/excel")
    public ResponseEntity<byte[]> exportExcel() {
        try {
            List<Booking> bookings = bookingRepository.findAll();
            byte[] excelData = excelService.exportBookingsToExcel(bookings);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
            headers.setContentDispositionFormData("attachment", "bookings.xlsx");
            
            return ResponseEntity.ok()
                    .headers(headers)
                    .body(excelData);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
    
    @GetMapping("/audit")
    public ResponseEntity<Page<Map<String, Object>>> getAuditLogs(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "50") int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<com.ticketbroker.model.AuditLog> logs = auditLogRepository.findAllByOrderByTimestampDesc(pageable);
        
        Page<Map<String, Object>> responses = logs.map(log -> {
            Map<String, Object> map = new HashMap<>();
            map.put("id", log.getId());
            map.put("timestamp", log.getTimestamp());
            map.put("actionType", log.getActionType());
            map.put("entityType", log.getEntityType());
            map.put("entityId", log.getEntityId());
            map.put("userType", log.getUserType());
            map.put("userIdentifier", log.getUserIdentifier());
            map.put("details", log.getDetails());
            return map;
        });
        
        return ResponseEntity.ok(responses);
    }
    
    @GetMapping("/settings")
    public ResponseEntity<Map<String, String>> getSettings() {
        Map<String, String> settings = new HashMap<>();
        settings.put("concertName", settingsService.getValue("concert_name", "Klasskonsert 24C"));
        settings.put("concertDate", settingsService.getValue("concert_date", "29/1 2026"));
        settings.put("concertVenue", settingsService.getValue("concert_venue", "Aulan på Rytmus Stockholm"));
        settings.put("adultPrice", settingsService.getValue("adult_ticket_price", "200"));
        settings.put("studentPrice", settingsService.getValue("student_ticket_price", "100"));
        settings.put("swishNumber", settingsService.getValue("swish_number", "012 345 67 89"));
        settings.put("swishRecipientName", settingsService.getValue("swish_recipient_name", "Event Organizer"));
        settings.put("contactEmail", settingsService.getValue("contact_email", "admin@example.com"));
        settings.put("adminEmail", settingsService.getValue("admin_email", "klasskonsertgruppen@gmail.com"));
        
        return ResponseEntity.ok(settings);
    }
    
    @PostMapping("/settings")
    public ResponseEntity<Map<String, String>> updateSettings(@RequestBody Map<String, String> settings) {
        for (Map.Entry<String, String> entry : settings.entrySet()) {
            settingsService.setValue(entry.getKey(), entry.getValue());
        }
        return ResponseEntity.ok(settings);
    }
}

