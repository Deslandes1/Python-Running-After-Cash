import pygame
import random
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Load sounds (create a simple bell sound using pygame's sine wave generator)
def create_bell_sound():
    sample_rate = 44100
    duration = 0.3
    frequency = 880  # A5 note
    samples = int(sample_rate * duration)
    wave = [int(32767 * 0.5 * (1 - abs(i / samples * 2 - 1)) * (i % 2) * 2) for i in range(samples)]  # simple beep
    sound = pygame.mixer.Sound(buffer=bytes(bytearray(wave)))
    return sound

bell_sound = create_bell_sound()

# Load images (create simple shapes instead of external files)
# We'll use pygame.draw functions for all graphics

# Game classes
class Snake:
    def __init__(self):
        self.width = 40
        self.height = 40
        self.x = 50
        self.y = SCREEN_HEIGHT - self.height - 30
        self.y_velocity = 0
        self.on_ground = True
        self.score = 0
        self.cash_collected = 0

    def jump(self):
        if self.on_ground:
            self.y_velocity = -12
            self.on_ground = False

    def update(self):
        # Gravity
        self.y_velocity += 0.8
        self.y += self.y_velocity
        if self.y >= SCREEN_HEIGHT - self.height - 30:
            self.y = SCREEN_HEIGHT - self.height - 30
            self.y_velocity = 0
            self.on_ground = True
        # Keep within screen top
        if self.y < 0:
            self.y = 0
            self.y_velocity = 0

    def draw(self, screen):
        # Draw snake head (green rectangle with eyes)
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
        pygame.draw.circle(screen, WHITE, (self.x + 10, self.y + 10), 5)
        pygame.draw.circle(screen, WHITE, (self.x + 30, self.y + 10), 5)
        pygame.draw.circle(screen, BLACK, (self.x + 10, self.y + 10), 2)
        pygame.draw.circle(screen, BLACK, (self.x + 30, self.y + 10), 2)
        # Tongue
        pygame.draw.line(screen, RED, (self.x + 40, self.y + 20), (self.x + 50, self.y + 25), 3)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Money:
    def __init__(self, x, y):
        self.width = 25
        self.height = 25
        self.x = x
        self.y = y
        self.collected = False

    def draw(self, screen):
        if not self.collected:
            pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))
            # Draw dollar sign
            font = pygame.font.Font(None, 24)
            text = font.render("$", True, BLACK)
            screen.blit(text, (self.x + 5, self.y + 2))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Car:
    def __init__(self, x, y):
        self.width = 60
        self.height = 40
        self.x = x
        self.y = y
        self.speed = -8  # moves left

    def update(self):
        self.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        pygame.draw.circle(screen, BLACK, (self.x + 15, self.y + 35), 8)
        pygame.draw.circle(screen, BLACK, (self.x + 45, self.y + 35), 8)
        pygame.draw.rect(screen, BLUE, (self.x + 10, self.y + 10, 40, 20))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Balloon:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.color = random.choice([RED, BLUE, YELLOW, ORANGE])
        self.speed = -2

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pygame.draw.line(screen, BLACK, (self.x, self.y + self.radius), (self.x, self.y + self.radius + 10), 2)

def show_game_over(screen, score):
    font = pygame.font.Font(None, 74)
    text = font.render("GAME OVER", True, RED)
    screen.blit(text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 50))
    font_small = pygame.font.Font(None, 36)
    score_text = font_small.render(f"Cash collected: {score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 20))
    pygame.display.flip()
    pygame.time.wait(3000)

def show_win(screen, score, balloons):
    # Draw balloons
    for balloon in balloons:
        balloon.draw(screen)
    # Congratulation text
    font = pygame.font.Font(None, 48)
    text = font.render("Congratulations! Pythoneer", True, YELLOW)
    screen.blit(text, (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 - 50))
    font_small = pygame.font.Font(None, 36)
    score_text = font_small.render(f"You collected {score} cash bags!", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 + 20))
    pygame.display.flip()
    pygame.time.wait(4000)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Python Running After Cash")
    clock = pygame.time.Clock()

    snake = Snake()
    # Money bags placed at increasing x positions
    money_bags = [
        Money(250, SCREEN_HEIGHT - 100),
        Money(450, SCREEN_HEIGHT - 130),
        Money(650, SCREEN_HEIGHT - 90),
        Money(850, SCREEN_HEIGHT - 120),
        Money(1050, SCREEN_HEIGHT - 100),
    ]
    # Cars appear periodically
    cars = []
    car_timer = 0
    finish_line_x = 1200  # after last money bag

    # Game state
    running = True
    game_over = False
    win = False
    balloons = []

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.jump()
                if game_over or win:
                    if event.key == pygame.K_r:
                        # Restart
                        return main()
                    if event.key == pygame.K_q:
                        running = False

        if not game_over and not win:
            # Update snake
            snake.update()

            # Update cars and spawn new cars
            car_timer += 1
            if car_timer > 90:  # spawn car every 1.5 seconds
                car_timer = 0
                cars.append(Car(SCREEN_WIDTH, SCREEN_HEIGHT - 70))
            for car in cars[:]:
                car.update()
                if car.x + car.width < 0:
                    cars.remove(car)

            # Check collision with car
            for car in cars:
                if snake.get_rect().colliderect(car.get_rect()):
                    game_over = True

            # Check collision with money bags
            for money in money_bags:
                if not money.collected and snake.get_rect().colliderect(money.get_rect()):
                    money.collected = True
                    snake.cash_collected += 1
                    bell_sound.play()
                    # Remove money bag after collection (optional, we just mark collected)
            
            # Check if all money bags collected
            if all(m.collected for m in money_bags):
                if snake.x + snake.width >= finish_line_x - 50:
                    win = True
                    # Create balloons
                    for i in range(20):
                        balloons.append(Balloon(random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT))
                else:
                    # Move snake automatically forward (only if not finished)
                    snake.x += 3

            # If snake passes finish line after collecting all money, win
            if snake.x + snake.width >= finish_line_x and all(m.collected for m in money_bags):
                win = True
                for i in range(20):
                    balloons.append(Balloon(random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT))

            # Prevent snake from going too far left
            if snake.x < 0:
                snake.x = 0

        # Drawing
        screen.fill(WHITE)
        # Draw ground
        pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT - 30, SCREEN_WIDTH, 30))
        pygame.draw.line(screen, WHITE, (0, SCREEN_HEIGHT - 30), (SCREEN_WIDTH, SCREEN_HEIGHT - 30), 2)

        # Draw finish line
        if all(m.collected for m in money_bags):
            pygame.draw.line(screen, BLUE, (finish_line_x, 0), (finish_line_x, SCREEN_HEIGHT), 5)
            font = pygame.font.Font(None, 24)
            finish_text = font.render("FINISH", True, BLUE)
            screen.blit(finish_text, (finish_line_x - 30, SCREEN_HEIGHT // 2))

        snake.draw(screen)
        for money in money_bags:
            money.draw(screen)
        for car in cars:
            car.draw(screen)

        # Score display
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Cash: {snake.cash_collected}/{len(money_bags)}", True, BLACK)
        screen.blit(score_text, (10, 10))

        if game_over:
            show_game_over(screen, snake.cash_collected)
            running = False
        if win:
            # Animate balloons
            for _ in range(3):
                for balloon in balloons:
                    balloon.update()
                screen.fill(WHITE)
                # redraw everything (simplified)
                pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT - 30, SCREEN_WIDTH, 30))
                snake.draw(screen)
                for money in money_bags:
                    money.draw(screen)
                for balloon in balloons:
                    balloon.draw(screen)
                font_large = pygame.font.Font(None, 48)
                congrats = font_large.render("Congratulations! Pythoneer", True, YELLOW)
                screen.blit(congrats, (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 - 50))
                pygame.display.flip()
                pygame.time.wait(100)
            pygame.time.wait(2000)
            running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
