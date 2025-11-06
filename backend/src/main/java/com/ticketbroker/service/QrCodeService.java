package com.ticketbroker.service;

import com.google.zxing.BarcodeFormat;
import com.google.zxing.EncodeHintType;
import com.google.zxing.WriterException;
import com.google.zxing.common.BitMatrix;
import com.google.zxing.qrcode.QRCodeWriter;
import com.google.zxing.qrcode.decoder.ErrorCorrectionLevel;
import org.springframework.stereotype.Service;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;

@Service
public class QrCodeService {
    private static final int QR_CODE_SIZE = 300;
    private static final int LOGO_SIZE = 45; // 15% of QR code size
    
    public String generateQrCodeBase64(String data) {
        try {
            BufferedImage qrImage = generateQrCodeImage(data, null);
            return imageToBase64(qrImage);
        } catch (Exception e) {
            throw new RuntimeException("Failed to generate QR code", e);
        }
    }
    
    public String generateQrCodeWithLogoBase64(String data, byte[] logoBytes) {
        try {
            BufferedImage logo = logoBytes != null ? ImageIO.read(new java.io.ByteArrayInputStream(logoBytes)) : null;
            BufferedImage qrImage = generateQrCodeImage(data, logo);
            return imageToBase64(qrImage);
        } catch (Exception e) {
            throw new RuntimeException("Failed to generate QR code with logo", e);
        }
    }
    
    private BufferedImage generateQrCodeImage(String data, BufferedImage logo) throws WriterException, IOException {
        Map<EncodeHintType, Object> hints = new HashMap<>();
        hints.put(EncodeHintType.ERROR_CORRECTION, ErrorCorrectionLevel.H);
        hints.put(EncodeHintType.CHARACTER_SET, "UTF-8");
        hints.put(EncodeHintType.MARGIN, 1);
        
        QRCodeWriter qrCodeWriter = new QRCodeWriter();
        BitMatrix bitMatrix = qrCodeWriter.encode(data, BarcodeFormat.QR_CODE, QR_CODE_SIZE, QR_CODE_SIZE, hints);
        
        BufferedImage qrImage = new BufferedImage(QR_CODE_SIZE, QR_CODE_SIZE, BufferedImage.TYPE_INT_RGB);
        Graphics2D graphics = qrImage.createGraphics();
        graphics.setColor(Color.WHITE);
        graphics.fillRect(0, 0, QR_CODE_SIZE, QR_CODE_SIZE);
        graphics.setColor(Color.BLACK);
        
        for (int x = 0; x < QR_CODE_SIZE; x++) {
            for (int y = 0; y < QR_CODE_SIZE; y++) {
                if (bitMatrix.get(x, y)) {
                    graphics.fillRect(x, y, 1, 1);
                }
            }
        }
        
        if (logo != null) {
            addLogoToQrCode(qrImage, logo);
        }
        
        graphics.dispose();
        return qrImage;
    }
    
    private void addLogoToQrCode(BufferedImage qrImage, BufferedImage logo) {
        Graphics2D graphics = qrImage.createGraphics();
        graphics.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        
        // Resize logo
        Image scaledLogo = logo.getScaledInstance(LOGO_SIZE, LOGO_SIZE, Image.SCALE_SMOOTH);
        BufferedImage logoBuffered = new BufferedImage(LOGO_SIZE, LOGO_SIZE, BufferedImage.TYPE_INT_ARGB);
        Graphics2D logoGraphics = logoBuffered.createGraphics();
        logoGraphics.drawImage(scaledLogo, 0, 0, null);
        logoGraphics.dispose();
        
        // Create semi-transparent white background
        BufferedImage logoBg = new BufferedImage(LOGO_SIZE + 8, LOGO_SIZE + 8, BufferedImage.TYPE_INT_ARGB);
        Graphics2D bgGraphics = logoBg.createGraphics();
        bgGraphics.setColor(new Color(255, 255, 255, 200));
        bgGraphics.fillRoundRect(0, 0, LOGO_SIZE + 8, LOGO_SIZE + 8, 4, 4);
        bgGraphics.dispose();
        
        // Paste logo on background
        Graphics2D bgGraphics2 = logoBg.createGraphics();
        bgGraphics2.drawImage(logoBuffered, 4, 4, null);
        bgGraphics2.dispose();
        
        // Center logo on QR code
        int x = (QR_CODE_SIZE - logoBg.getWidth()) / 2;
        int y = (QR_CODE_SIZE - logoBg.getHeight()) / 2;
        graphics.drawImage(logoBg, x, y, null);
        graphics.dispose();
    }
    
    private String imageToBase64(BufferedImage image) throws IOException {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        ImageIO.write(image, "PNG", baos);
        return Base64.getEncoder().encodeToString(baos.toByteArray());
    }
}

