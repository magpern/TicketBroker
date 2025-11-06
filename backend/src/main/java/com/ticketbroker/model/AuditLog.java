package com.ticketbroker.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "audit_logs")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AuditLog {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, updatable = false)
    private LocalDateTime timestamp = LocalDateTime.now();
    
    @Column(nullable = false, length = 50)
    private String actionType; // booking_created, payment_initiated, etc.
    
    @Column(nullable = false, length = 20)
    private String entityType; // booking, ticket, payment
    
    @Column(nullable = false)
    private Long entityId;
    
    @Column(nullable = false, length = 20)
    private String userType; // buyer, admin
    
    @Column(nullable = false, length = 50)
    private String userIdentifier; // Phone number or admin username
    
    @Column(columnDefinition = "TEXT")
    private String details; // JSON string for additional context
    
    @Column(columnDefinition = "TEXT")
    private String oldValue; // JSON string for before state
    
    @Column(columnDefinition = "TEXT")
    private String newValue; // JSON string for after state
}

