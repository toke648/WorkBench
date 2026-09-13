// 12
class shi {
    public static void main(String[] args) {
        int a = 10;
        int b = 2;
        int c = 0;
        try {
            c = a / b;
        } catch (ArithmeticException e) {
            System.out.println("Divide by zero");
        }
        System.out.println("Result: " + c);
    }
}
