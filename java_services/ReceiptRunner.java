import java.util.Map;
import java.util.HashMap;

public class ReceiptRunner {
    public static void main(String[] args) {
        if (args.length > 0) {
            String jsonData = args[0];
            System.out.println("Processing receipt for: " + jsonData);
            
            Map<String, Object> bookingData = parseJsonToMap(jsonData);
            
            String receipt = ReceiptGenerator.generateDigitalReceipt(bookingData);
            System.out.println(receipt);
            
            // Save to file
            Object receiptNum = bookingData.get("receipt_number");
            String filename = "receipt_" + (receiptNum != null ? receiptNum : "unknown") + ".txt";
            ReceiptGenerator.saveReceiptToFile(bookingData, filename);
            System.out.println("Receipt saved to: " + filename);
        } else {
            System.out.println("No data provided. Usage: java ReceiptRunner '{json data}'");
        }
    }
    
    private static Map<String, Object> parseJsonToMap(String json) {
        Map<String, Object> map = new HashMap<>();
        
        // Remove whitespace and trim
        json = json.trim();
        
        // Remove curly braces
        if (json.startsWith("{") && json.endsWith("}")) {
            json = json.substring(1, json.length() - 1);
        }
        
        // Handle empty json
        if (json.isEmpty()) {
            return map;
        }
        
        // Split by commas not inside quotes
        String[] pairs = json.split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)");
        
        for (String pair : pairs) {
            String[] keyValue = pair.split(":(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", 2);
            if (keyValue.length == 2) {
                String key = cleanString(keyValue[0]);
                String value = cleanString(keyValue[1]);
                
                // Try to parse as number
                try {
                    if (value.contains(".")) {
                        map.put(key, Double.parseDouble(value));
                    } else {
                        map.put(key, Integer.parseInt(value));
                    }
                } catch (NumberFormatException e) {
                    map.put(key, value);
                }
            }
        }
        
        return map;
    }
    
    private static String cleanString(String str) {
        str = str.trim();
        if (str.startsWith("\"") && str.endsWith("\"")) {
            str = str.substring(1, str.length() - 1);
        }
        return str;
    }
}