import java.util.Scanner;

public class stupid_shi {
    public static void main(String[] args) {
        int tries = 5;
        int randomnumber = (int) (Math.random() * 100) + 1;
        Scanner inputreader = new Scanner(System.in);
        while (tries > 0) {
            System.out.println("ha well enter your guess you plonker:");
            int guess = inputreader.nextInt();
            if (guess == randomnumber) {
                System.out.println("ha correct guess");
                break;
            } else if (guess > randomnumber) {
                System.out.println("too high try again");
                tries -= 1;
            } else {
                System.out.println("too low");
                tries -= 1;
            }
        }
        inputreader.close();
        if (tries == 0) {
            System.out.println("well you ran out of tries better luck next time");
            System.out.println("well the number was " + randomnumber);
        }
    }

}
