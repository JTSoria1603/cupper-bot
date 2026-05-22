#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "cupper_motor_controller.h"

void app_main(void)
{
    motor_controller_init();

    motor_set_all(40, 40, 40, 40);
    vTaskDelay(pdMS_TO_TICKS(2000));

    motor_stop_all();
}