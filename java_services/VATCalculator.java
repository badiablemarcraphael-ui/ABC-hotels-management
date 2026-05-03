import java.math.BigDecimal;
import java.math.RoundingMode;

public class VATCalculator {
    private static final double VAT_RATE = 0.07; // 7% VAT
    
    public static double calculateVAT(double amount) {
        BigDecimal vat = BigDecimal.valueOf(amount * VAT_RATE);
        return vat.setScale(2, RoundingMode.HALF_UP).doubleValue();
    }
    
    public static double calculateTotalWithVAT(double amount) {
        return amount + calculateVAT(amount);
    }
    
    public static VATResult calculateDetailedVAT(double subtotal, double serviceCharge, double tax) {
        VATResult result = new VATResult();
        result.subtotal = subtotal;
        result.vatOnSubtotal = calculateVAT(subtotal);
        result.vatOnService = calculateVAT(serviceCharge);
        result.totalVAT = result.vatOnSubtotal + result.vatOnService;
        result.grandTotal = subtotal + serviceCharge + tax + result.totalVAT;
        return result;
    }
    
    public static class VATResult {
        public double subtotal;
        public double vatOnSubtotal;
        public double vatOnService;
        public double totalVAT;
        public double grandTotal;
    }
}