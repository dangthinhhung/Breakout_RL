import pygame
import random
from collections import namedtuple

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

Point = namedtuple('Point', 'x, y')

# Colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Game settings
BRICK_WIDTH = 80
BRICK_HEIGHT = 30
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 10
BALL_RADIUS = 10
BALL_SPEED = 5  # Reduced ball speed
PADDLE_SPEED = 20  # Moderate paddle speed
FRAME_RATE = 60  # Frame rate

class BreakoutGameAI:
    def __init__(self, w=800, h=600):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Breakout')
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.paddle = Point(self.w / 2 - PADDLE_WIDTH / 2, self.h - 20)
        self.ball = Point(self.w / 2, self.h / 2)
        self.ball_vel = [BALL_SPEED, -BALL_SPEED]
        self.bricks = [Point(x, y) for x in range(0, self.w, BRICK_WIDTH + 5) for y in range(0, self.h // 3, BRICK_HEIGHT + 5)]
        self.total_bricks = len(self.bricks)
        self.score = 0
        self.hits = 0  # Track number of hits for reward calculation
        self.frame_iteration = 0

    def play_step(self, action):
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self._move_paddle(action)
        self._move_ball()

        reward = 0
        game_over = False

        if self._is_collision():
            reward = -10
            game_over = True
            return reward, game_over, self.score

        if self._break_brick():
            reward = 1

        if self.ball.y >= self.h:
            reward = -10
            game_over = True
            return reward, game_over, self.score

        if self.paddle.x <= self.ball.x <= self.paddle.x + PADDLE_WIDTH and self.paddle.y <= self.ball.y + BALL_RADIUS <= self.paddle.y + PADDLE_HEIGHT:
            self.hits += 1
            if self.hits > 1:  # Start rewarding from the second hit
                if self.ball_vel[1] > 0:
                    reward = 10
                    self.ball_vel[1] = -self.ball_vel[1]
                else:
                    reward = 3

        self.score = (self.total_bricks - len(self.bricks)) / self.total_bricks

        self._update_ui()
        self.clock.tick(FRAME_RATE)
        return reward, game_over, self.score

    def _move_paddle(self, action):
        if action == [1, 0, 0]:  # Move left
            self.paddle = Point(max(0, self.paddle.x - PADDLE_SPEED), self.paddle.y)
        elif action == [0, 1, 0]:  # Move right
            self.paddle = Point(min(self.w - PADDLE_WIDTH, self.paddle.x + PADDLE_SPEED), self.paddle.y)
        elif action == [0, 0, 1]:  # Stay still
            pass

    def _move_ball(self):
        x, y = self.ball
        vx, vy = self.ball_vel
        x += vx
        y += vy

        if x <= 0 or x >= self.w - BALL_RADIUS:
            vx = -vx
        if y <= 0:
            vy = -vy

        self.ball = Point(x, y)
        self.ball_vel = [vx, vy]

    def _break_brick(self):
        for brick in self.bricks:
            if brick.x <= self.ball.x <= brick.x + BRICK_WIDTH and brick.y <= self.ball.y <= brick.y + BRICK_HEIGHT:
                self.bricks.remove(brick)
                self.ball_vel[1] = -self.ball_vel[1]
                return True
        return False

    def _is_collision(self):
        return self.ball.y > self.h

    def _update_ui(self):
        self.display.fill(BLACK)
        pygame.draw.rect(self.display, BLUE, pygame.Rect(self.paddle.x, self.paddle.y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.circle(self.display, RED, (int(self.ball.x), int(self.ball.y)), BALL_RADIUS)
        for brick in self.bricks:
            pygame.draw.rect(self.display, WHITE, pygame.Rect(brick.x, brick.y, BRICK_WIDTH, BRICK_HEIGHT))
        score_text = font.render("Score: {:.2f}".format(self.score), True, WHITE)
        self.display.blit(score_text, [0, 0])
        pygame.display.flip()
