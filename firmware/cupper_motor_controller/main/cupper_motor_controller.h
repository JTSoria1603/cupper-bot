// cupper_motor_controller.h

#pragma once

#include "driver/gpio.h"

// Front Left
#define MOTOR_FL_IN1 GPIO_NUM_4
#define MOTOR_FL_IN2 GPIO_NUM_5
#define MOTOR_FL_PWM GPIO_NUM_6

// Front Right
#define MOTOR_FR_IN1 GPIO_NUM_7
#define MOTOR_FR_IN2 GPIO_NUM_15
#define MOTOR_FR_PWM GPIO_NUM_16

// Rear Left
#define MOTOR_RL_IN1 GPIO_NUM_8
#define MOTOR_RL_IN2 GPIO_NUM_9
#define MOTOR_RL_PWM GPIO_NUM_10

// Rear Right
#define MOTOR_RR_IN1 GPIO_NUM_11
#define MOTOR_RR_IN2 GPIO_NUM_12
#define MOTOR_RR_PWM GPIO_NUM_13

typedef enum {
    MOTOR_FRONT_LEFT = 0,
    MOTOR_FRONT_RIGHT,
    MOTOR_REAR_LEFT,
    MOTOR_REAR_RIGHT,
    MOTOR_COUNT
} motor_id_t;

void motor_controller_init(void);

void motor_set_speed(motor_id_t motor_id, int speed);

void motor_set_all(int fl, int fr, int rl, int rr);

void motor_stop(motor_id_t motor_id);

void motor_stop_all(void);