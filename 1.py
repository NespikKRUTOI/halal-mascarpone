import pygame
import random
import sys
import time

pygame.init()
from settings import *


class SimpleMinesweeper:
    def __init__(self):
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption('Сапер — мінімал')
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 40)
        self.reset()

    def reset(self):
        self.board = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.revealed = [[False for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.flagged = [[False for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.first = True
        self.game_over = False
        self.won = False
        self.start = None
        self.end_time = None
        # restart button rect
        btn_w, btn_h = 90, 34
        btn_x = MARGIN
        btn_y = (TOPBAR - btn_h) // 2
        self.restart_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

    def place_mines(self, safe=None):
        placed = 0
        safe_set = set()
        if safe:
            sx, sy = safe
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    safe_set.add((sx + dx, sy + dy))
        while placed < MINES:
            x = random.randrange(WIDTH)
            y = random.randrange(HEIGHT)
            if (x, y) in safe_set:
                continue
            if self.board[y][x] != -1:
                self.board[y][x] = -1
                placed += 1

    def calc(self):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.board[y][x] == -1:
                    continue
                c = 0
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and self.board[ny][nx] == -1:
                            c += 1
                self.board[y][x] = c

    def reveal(self, x, y):
        if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
            return
        if self.revealed[y][x] or self.flagged[y][x] or self.game_over:
            return
        if self.first:
            self.place_mines(safe=(x, y))
            self.calc()
            self.start = time.time()
            self.first = False

        self.revealed[y][x] = True
        if self.board[y][x] == -1:
            self.game_over = True
            self.end_time = time.time()
            self.reveal_all_mines()
            return
        # flood for zeros
        if self.board[y][x] == 0:
            stack = [(x, y)]
            while stack:
                cx, cy = stack.pop()
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and not self.revealed[ny][nx] and not self.flagged[ny][nx]:
                            self.revealed[ny][nx] = True
                            if self.board[ny][nx] == 0:
                                stack.append((nx, ny))

    def reveal_all_mines(self):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.board[y][x] == -1:
                    self.revealed[y][x] = True

    def reveal_adjacent(self, x, y):
        """Reveal neighboring covered cells only when flagged count equals cell number."""
        # count adjacent flags
        flag_count = 0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and self.flagged[ny][nx]:
                    flag_count += 1

        # Only allow opening neighbors when there are flags and the number matches
        val = self.board[y][x]
        if val <= 0:
            return
        if flag_count == 0 or flag_count != val:
            return

        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and not self.revealed[ny][nx] and not self.flagged[ny][nx]:
                    self.reveal(nx, ny)

    def toggle_flag(self, x, y):
        if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
            return
        if self.revealed[y][x] or self.game_over:
            return
        self.flagged[y][x] = not self.flagged[y][x]

    def coord(self, mx, my):
        grid_top = TOPBAR + MARGIN
        if mx < MARGIN or my < grid_top:
            return None
        gx = (mx - MARGIN) // CELL
        gy = (my - grid_top) // CELL
        if 0 <= gx < WIDTH and 0 <= gy < HEIGHT:
            return gx, gy
        return None

    def check_win(self):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.board[y][x] != -1 and not self.revealed[y][x]:
                    return False
        self.won = True
        self.game_over = True
        self.end_time = time.time()
        return True

    def draw(self):
        # background and top bar
        self.screen.fill(BG)
        top_rect = pygame.Rect(0, 0, SCREEN_W, TOPBAR)
        pygame.draw.rect(self.screen, TOP_BG, top_rect)

        # restart button (hover effect)
        mx, my = pygame.mouse.get_pos()
        hover = self.restart_rect.collidepoint(mx, my)
        btn_color = (210, 210, 210) if hover else COVER
        pygame.draw.rect(self.screen, btn_color, self.restart_rect)
        pygame.draw.rect(self.screen, GRID, self.restart_rect, 2)
        text = self.font.render('Рестарт', True, NUM_COLOR)
        tx = self.restart_rect.centerx - text.get_width() // 2
        ty = self.restart_rect.centery - text.get_height() // 2
        self.screen.blit(text, (tx, ty))

        # mines left counter (right side)
        flags = sum(sum(1 for f in row if f) for row in self.flagged)
        mines_left = max(0, MINES - flags)
        counter_text = self.font.render(f'Міни: {mines_left}', True, NUM_COLOR)
        cx = SCREEN_W - MARGIN - counter_text.get_width()
        cy = (TOPBAR - counter_text.get_height()) // 2
        self.screen.blit(counter_text, (cx, cy))

        # timer (to the right of restart)
        if self.start is None:
            elapsed = 0
        else:
            end = self.end_time if self.end_time is not None else time.time()
            elapsed = int(end - self.start)
        mins = elapsed // 60
        secs = elapsed % 60
        timer_text = self.font.render(f'{mins}:{secs:02d}', True, NUM_COLOR)
        tx2 = self.restart_rect.right + 12
        ty2 = (TOPBAR - timer_text.get_height()) // 2
        self.screen.blit(timer_text, (tx2, ty2))

        # draw cells (below the top bar)
        for y in range(HEIGHT):
            for x in range(WIDTH):
                rx = MARGIN + x * CELL
                ry = TOPBAR + MARGIN + y * CELL
                rect = pygame.Rect(rx, ry, CELL - 1, CELL - 1)
                if self.revealed[y][x]:
                    pygame.draw.rect(self.screen, OPEN, rect)
                    # mine
                    if self.board[y][x] == -1:
                        pygame.draw.circle(self.screen, MINE, rect.center, CELL // 4)
                    # number
                    elif self.board[y][x] > 0:
                        num = self.board[y][x]
                        color = NUM_COLORS.get(num, NUM_COLOR)
                        ntext = self.font.render(str(num), True, color)
                        nx = rect.centerx - ntext.get_width() // 2
                        ny = rect.centery - ntext.get_height() // 2
                        self.screen.blit(ntext, (nx, ny))
                else:
                    pygame.draw.rect(self.screen, COVER, rect)
                    if self.flagged[y][x]:
                        fr = pygame.Rect(0, 0, CELL // 2, CELL // 2)
                        fr.center = rect.center
                        pygame.draw.rect(self.screen, FLAG, fr)
                pygame.draw.rect(self.screen, GRID, rect, 1)

        # draw result overlay if game over
        if self.game_over:
            if self.won:
                msg = 'Ви виграли!'
                color = (10, 150, 10)
            else:
                msg = 'Ви програли!'
                color = (150, 10, 10)

            msg_surf = self.big_font.render(msg, True, color)
            pad = 18
            w = msg_surf.get_width() + pad * 2
            h = msg_surf.get_height() + pad * 2
            r = pygame.Rect((SCREEN_W - w) // 2, (SCREEN_H - h) // 2, w, h)
            pygame.draw.rect(self.screen, (240, 240, 240), r)
            pygame.draw.rect(self.screen, GRID, r, 2)
            self.screen.blit(msg_surf, (r.x + pad, r.y + pad))

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            clock.tick(60)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    # check restart click
                    if self.restart_rect.collidepoint(mx, my):
                        self.reset()
                        continue

                    pos = self.coord(mx, my)
                    if pos is None:
                        continue
                    x, y = pos
                    if ev.button == 1:
                        # if cell already revealed, reveal its neighbors
                        if self.revealed[y][x]:
                            self.reveal_adjacent(x, y)
                        else:
                            self.reveal(x, y)
                        if not self.game_over:
                            self.check_win()
                    elif ev.button == 3:
                        self.toggle_flag(x, y)
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_r:
                        self.reset()

            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    game = SimpleMinesweeper()
    game.run()
