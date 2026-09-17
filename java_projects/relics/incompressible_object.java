public class incompressible_object {
    public static void main(String[] args) {
        int x_limits = 20;
        int y_limits = 20;
        double object_pos_x = 10;
        double object_pos_y = 10;
        double velocity_x = 100;
        double velocity_y = 120;
        double elastic_loss_factor_percentage = 0.1;
        for (int tick = 0; tick < 100; tick++) {
            object_pos_x += velocity_x;
            object_pos_y += velocity_y;
            if (object_pos_x >= x_limits) {
                object_pos_x = x_limits;
                velocity_x -= elastic_loss_factor_percentage * velocity_x;
                velocity_x = -velocity_x;
            }
            if (object_pos_y >= y_limits) {
                object_pos_y = y_limits;
                velocity_y -= elastic_loss_factor_percentage * velocity_y;
                velocity_y = -velocity_y;
            }
            if (object_pos_x <= 0) {
                object_pos_x = 0;
                velocity_x += elastic_loss_factor_percentage * velocity_x;
                velocity_x = -velocity_x;
            }
            if (object_pos_y <= 0) {
                object_pos_y = 0;
                velocity_y += elastic_loss_factor_percentage * velocity_y;
                velocity_y = -velocity_y;
            }
            System.out.println("position x is:" + object_pos_x);
            System.out.println("position y is :" + object_pos_y);
            System.err.println("x speed is :" + velocity_x);
            System.out.println("y speed is :" + velocity_y);

        }
        System.err.println("simulation_done");
    }

}
