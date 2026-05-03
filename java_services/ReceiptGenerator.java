import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;

public class ReceiptGenerator {
    
    public static String generateDigitalReceipt(Map<String, Object> bookingDetails) {
        StringBuilder receipt = new StringBuilder();
        
        receipt.append("=".repeat(50)).append("\n");
        receipt.append("           HOTEL MANAGEMENT SYSTEM\n");
        receipt.append("           DIGITAL RECEIPT\n");
        receipt.append("=".repeat(50)).append("\n\n");
        
        // Receipt Header
        receipt.append("Receipt #: ").append(getStringValue(bookingDetails.get("receipt_number"))).append("\n");
        receipt.append("Date: ").append(LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))).append("\n\n");
        
        // Guest Details
        receipt.append("GUEST DETAILS:\n");
        receipt.append("-".repeat(30)).append("\n");
        receipt.append("Name: ").append(getStringValue(bookingDetails.get("guest_name"))).append("\n");
        receipt.append("Email: ").append(getStringValue(bookingDetails.get("guest_email"))).append("\n");
        receipt.append("Phone: ").append(getStringValue(bookingDetails.get("guest_phone"))).append("\n\n");
        
        // Booking Details
        receipt.append("BOOKING DETAILS:\n");
        receipt.append("-".repeat(30)).append("\n");
        receipt.append("Room: ").append(getStringValue(bookingDetails.get("room_number"))).append("\n");
        receipt.append("Check-in: ").append(getStringValue(bookingDetails.get("check_in"))).append("\n");
        receipt.append("Check-out: ").append(getStringValue(bookingDetails.get("check_out"))).append("\n");
        receipt.append("Nights: ").append(getStringValue(bookingDetails.get("nights"))).append("\n\n");
        
        // Price Breakdown - Safe number extraction
        Double roomRate = getDoubleValue(bookingDetails.get("room_rate"));
        Integer nights = getIntegerValue(bookingDetails.get("nights"));
        Double subtotal = getDoubleValue(bookingDetails.get("subtotal"));
        Double vat = getDoubleValue(bookingDetails.get("vat"));
        Double serviceCharge = getDoubleValue(bookingDetails.get("service_charge"));
        Double total = getDoubleValue(bookingDetails.get("total"));
        
        receipt.append("PRICE BREAKDOWN:\n");
        receipt.append("-".repeat(30)).append("\n");
        receipt.append(String.format("Room Rate: $%.2f x %d nights\n", roomRate, nights));
        receipt.append(String.format("Subtotal: $%.2f\n", subtotal));
        receipt.append(String.format("VAT (7%%): $%.2f\n", vat));
        receipt.append(String.format("Service Charge: $%.2f\n", serviceCharge));
        receipt.append("-".repeat(30)).append("\n");
        receipt.append(String.format("TOTAL: $%.2f\n", total));
        
        receipt.append("\n").append("=".repeat(50)).append("\n");
        receipt.append("     Thank you for choosing us!\n");
        receipt.append("     For inquiries, call: +1-234-567-8900\n");
        receipt.append("=".repeat(50));
        
        return receipt.toString();
    }
    
    public static void saveReceiptToFile(Map<String, Object> bookingDetails, String filename) {
        String receipt = generateDigitalReceipt(bookingDetails);
        try {
            java.nio.file.Files.write(java.nio.file.Paths.get(filename), receipt.getBytes());
            System.out.println("Receipt saved to: " + filename);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    private static String getStringValue(Object value) {
        return value != null ? value.toString() : "";
    }
    
    private static Double getDoubleValue(Object value) {
        if (value == null) return 0.0;
        if (value instanceof Double) return (Double) value;
        if (value instanceof Integer) return ((Integer) value).doubleValue();
        if (value instanceof String) {
            try {
                return Double.parseDouble((String) value);
            } catch (NumberFormatException e) {
                return 0.0;
            }
        }
        return 0.0;
    }
    
    private static Integer getIntegerValue(Object value) {
        if (value == null) return 0;
        if (value instanceof Integer) return (Integer) value;
        if (value instanceof String) {
            try {
                return Integer.parseInt((String) value);
            } catch (NumberFormatException e) {
                return 0;
            }
        }
        return 0;
    }
}