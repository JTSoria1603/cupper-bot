// cupper_motor_controller.c

#include "cupper_motor_controller.h"

#include "driver/gpio.h"
#include "driver/ledc.h"
#include "esp_log.h"

#define PWM_TIMER              LEDC_TIMER_0
#define PWM_MODE               LEDC_LOW_SPEED_MODE
#define PWM_FREQ_HZ            1000
#define PWM_RESOLUTION         LEDC_TIMER_10_BIT
#define PWM_MAX_DUTY           1023

static const char *TAG = "CupperMotor";

typedef struct {
    gpio_num_t in1;
    gpio_num_t in2;
    gpio_num_t pwm_gpio;
    ledc_channel_t pwm_channel;
} motor_t;

static motor_t motors[MOTOR_COUNT] = {
    [MOTOR_FRONT_LEFT] = {
        .in1 = MOTOR_FL_IN1,
        .in2 = MOTOR_FL_IN2,
        .pwm_gpio = MOTOR_FL_PWM,
        .pwm_channel = LEDC_CHANNEL_0,
    },
    [MOTOR_FRONT_RIGHT] = {
        .in1 = MOTOR_FR_IN1,
        .in2 = MOTOR_FR_IN2,
        .pwm_gpio = MOTOR_FR_PWM,
        .pwm_channel = LEDC_CHANNEL_1,
    },
    [MOTOR_REAR_LEFT] = {
        .in1 = MOTOR_RL_IN1,
        .in2 = MOTOR_RL_IN2,
        .pwm_gpio = MOTOR_RL_PWM,
        .pwm_channel = LEDC_CHANNEL_2,
    },
    [MOTOR_REAR_RIGHT] = {
        .in1 = MOTOR_RR_IN1,
        .in2 = MOTOR_RR_IN2,
        .pwm_gpio = MOTOR_RR_PWM,
        .pwm_channel = LEDC_CHANNEL_3,
    },
};

static uint32_t speed_to_duty(int speed)
{
    if (speed < 0) {
        speed = -speed;
    }

    if (speed > 100) {
        speed = 100;
    }

    return (speed * PWM_MAX_DUTY) / 100;
}

void motor_controller_init(void)
{
    gpio_config_t io_conf = {
        .pin_bit_mask = 0,
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };

    for (int i = 0; i < MOTOR_COUNT; i++) {
        io_conf.pin_bit_mask |= (1ULL << motors[i].in1);
        io_conf.pin_bit_mask |= (1ULL << motors[i].in2);
    }

    gpio_config(&io_conf);

    ledc_timer_config_t timer_conf = {
        .speed_mode = PWM_MODE,
        .timer_num = PWM_TIMER,
        .duty_resolution = PWM_RESOLUTION,
        .freq_hz = PWM_FREQ_HZ,
        .clk_cfg = LEDC_AUTO_CLK,
    };

    ledc_timer_config(&timer_conf);

    for (int i = 0; i < MOTOR_COUNT; i++) {
        ledc_channel_config_t channel_conf = {
            .gpio_num = motors[i].pwm_gpio,
            .speed_mode = PWM_MODE,
            .channel = motors[i].pwm_channel,
            .intr_type = LEDC_INTR_DISABLE,
            .timer_sel = PWM_TIMER,
            .duty = 0,
            .hpoint = 0,
        };

        ledc_channel_config(&channel_conf);

        gpio_set_level(motors[i].in1, 0);
        gpio_set_level(motors[i].in2, 0);
    }

    ESP_LOGI(TAG, "Motor controller initialized");
}

void motor_set_speed(motor_id_t motor_id, int speed)
{
    if (motor_id < 0 || motor_id >= MOTOR_COUNT) {
        ESP_LOGE(TAG, "Invalid motor id: %d", motor_id);
        return;
    }

    if (speed > 100) {
        speed = 100;
    } else if (speed < -100) {
        speed = -100;
    }

    motor_t *motor = &motors[motor_id];
    uint32_t duty = speed_to_duty(speed);

    if (speed > 0) {
        gpio_set_level(motor->in1, 1);
        gpio_set_level(motor->in2, 0);
    } else if (speed < 0) {
        gpio_set_level(motor->in1, 0);
        gpio_set_level(motor->in2, 1);
    } else {
        gpio_set_level(motor->in1, 0);
        gpio_set_level(motor->in2, 0);
    }

    ledc_set_duty(PWM_MODE, motor->pwm_channel, duty);
    ledc_update_duty(PWM_MODE, motor->pwm_channel);
}

void motor_set_all(int fl, int fr, int rl, int rr)
{
    motor_set_speed(MOTOR_FRONT_LEFT, fl);
    motor_set_speed(MOTOR_FRONT_RIGHT, fr);
    motor_set_speed(MOTOR_REAR_LEFT, rl);
    motor_set_speed(MOTOR_REAR_RIGHT, rr);
}

void motor_stop(motor_id_t motor_id)
{
    motor_set_speed(motor_id, 0);
}

void motor_stop_all(void)
{
    motor_set_all(0, 0, 0, 0);
}