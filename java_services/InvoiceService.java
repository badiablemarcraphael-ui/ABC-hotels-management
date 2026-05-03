import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;

@SuppressWarnings("unchecked")
public class InvoiceService {
    
    public static String generateInvoice(Map<String, Object> invoiceData) {
        StringBuilder invoice = new StringBuilder();
        
        invoice.append("=".repeat(60)).append("\n");
        invoice.append("                  TAX INVOICE\n");
        invoice.append("=".repeat(60)).append("\n\n");
        
        // Company Info
        invoice.append("HOTEL MANAGEMENT SYSTEM\n");
        invoice.append("123 Business Street, City, Country\n");
        invoice.append("GST/VAT: XX1234567890\n");
        invoice.append("Phone: +1-234-567-8900\n\n");
        
        // Invoice Info
        invoice.append("INVOICE #: ").append(invoiceData.get("invoice_number")).append("\n");
        invoice.append("Date: ").append(LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd"))).append("\n");
        invoice.append("Due Date: ").append(invoiceData.get("due_date")).append("\n\n");
        
        // Bill To
        invoice.append("BILL TO:\n");
        invoice.append("-".repeat(30)).append("\n");
        invoice.append(invoiceData.get("guest_name")).append("\n");
        invoice.append(invoiceData.get("guest_email")).append("\n");
        invoice.append(invoiceData.get("guest_phone")).append("\n\n");
        
        // Items
        invoice.append("DESCRIPTION                    QTY    RATE     AMOUNT\n");
        invoice.append("-".repeat(60)).append("\n");
        
        // Safe cast with null check
        Object itemsObj = invoiceData.get("items");
        if (itemsObj instanceof Map) {
            Map<String, Object> items = (Map<String, Object>) itemsObj;
            for (Map.Entry<String, Object> item : items.entrySet()) {
                Object valueObj = item.getValue();
                if (valueObj instanceof Map) {
                    Map<String, Object> itemDetails = (Map<String, Object>) valueObj;
                    Integer qty = itemDetails.containsKey("qty") ? (Integer) itemDetails.get("qty") : 0;
                    Double rate = itemDetails.containsKey("rate") ? (Double) itemDetails.get("rate") : 0.0;
                    Double amount = itemDetails.containsKey("amount") ? (Double) itemDetails.get("amount") : 0.0;
                    
                    invoice.append(String.format("%-30s %3d   $%6.2f   $%7.2f\n", 
                        item.getKey(), qty, rate, amount));
                }
            }
        }
        
        invoice.append("-".repeat(60)).append("\n");
        
        // Safe number extraction
        Double subtotal = getDoubleValue(invoiceData.get("subtotal"));
        Double vat = getDoubleValue(invoiceData.get("vat"));
        Double total = getDoubleValue(invoiceData.get("total"));
        
        invoice.append(String.format("%-46s $%8.2f\n", "Subtotal:", subtotal));
        invoice.append(String.format("%-46s $%8.2f\n", "VAT (7%):", vat));
        invoice.append(String.format("%-46s $%8.2f\n", "Total:", total));
        invoice.append("=".repeat(60)).append("\n");
        invoice.append("              THANK YOU FOR YOUR BUSINESS!\n");
        invoice.append("=".repeat(60));
        
        return invoice.toString();
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
}