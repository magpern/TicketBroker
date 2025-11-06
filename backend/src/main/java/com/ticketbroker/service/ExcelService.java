package com.ticketbroker.service;

import com.ticketbroker.model.Booking;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.stereotype.Service;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Service
public class ExcelService {
    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");
    
    public byte[] exportBookingsToExcel(List<Booking> bookings) throws IOException {
        try (Workbook workbook = new XSSFWorkbook()) {
            Sheet sheet = workbook.createSheet("Bookings");
            
            // Create header row
            Row headerRow = sheet.createRow(0);
            String[] headers = {
                "ID", "Booking Reference", "First Name", "Last Name", "Email", "Phone",
                "Show Time", "Adult Tickets", "Student Tickets", "Total Amount",
                "Status", "Created At", "Confirmed At"
            };
            
            CellStyle headerStyle = workbook.createCellStyle();
            Font headerFont = workbook.createFont();
            headerFont.setBold(true);
            headerStyle.setFont(headerFont);
            headerStyle.setFillForegroundColor(IndexedColors.GREY_25_PERCENT.getIndex());
            headerStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
            
            for (int i = 0; i < headers.length; i++) {
                Cell cell = headerRow.createCell(i);
                cell.setCellValue(headers[i]);
                cell.setCellStyle(headerStyle);
            }
            
            // Create data rows
            int rowNum = 1;
            for (Booking booking : bookings) {
                Row row = sheet.createRow(rowNum++);
                
                row.createCell(0).setCellValue(booking.getId());
                row.createCell(1).setCellValue(booking.getBookingReference());
                row.createCell(2).setCellValue(booking.getFirstName());
                row.createCell(3).setCellValue(booking.getLastName());
                row.createCell(4).setCellValue(booking.getEmail());
                row.createCell(5).setCellValue(booking.getPhone());
                row.createCell(6).setCellValue(booking.getShow().getStartTime() + "-" + booking.getShow().getEndTime());
                row.createCell(7).setCellValue(booking.getAdultTickets());
                row.createCell(8).setCellValue(booking.getStudentTickets());
                row.createCell(9).setCellValue(booking.getTotalAmount());
                row.createCell(10).setCellValue(booking.getStatus());
                row.createCell(11).setCellValue(booking.getCreatedAt() != null ? 
                    booking.getCreatedAt().format(DATE_FORMATTER) : "");
                row.createCell(12).setCellValue(booking.getConfirmedAt() != null ? 
                    booking.getConfirmedAt().format(DATE_FORMATTER) : "");
            }
            
            // Auto-size columns
            for (int i = 0; i < headers.length; i++) {
                sheet.autoSizeColumn(i);
            }
            
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            workbook.write(baos);
            return baos.toByteArray();
        }
    }
}

