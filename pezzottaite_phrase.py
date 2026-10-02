#!/usr/bin/env python3
"""Pezzottaite Phrase — neon word-catch arcade for ElbowOS. Python 3 + pygame."""
import math, os, random, shutil, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/home/workdir/artifacts/PEZZOTTAITE_PHRASE_ElbowOS.mp4")
ALT = "/workspace/artifacts/PEZZOTTAITE_PHRASE_ElbowOS.mp4"
WORDS = ["REEL", "NEON", "ELBOW", "PRISM", "CHROMA", "ARCADE", "PULSE", "OS"]
LANES = 6
RASPB = (255, 72, 140)
GOLD = (255, 210, 96)
TEAL = (72, 236, 214)
MIST = (255, 220, 238)
VIO = (168, 92, 255)


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY and not RECORD else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        pygame.display.set_caption("Pezzottaite Phrase")
        self.big = pygame.font.SysFont("dejavusans", 54, bold=True)
        self.mid = pygame.font.SysFont("dejavusans", 46, bold=True)
        self.small = pygame.font.SysFont("dejavusans", 34, bold=True)
        self.tiny = pygame.font.SysFont("dejavusans", 28, bold=True)
        self.bg = self._bg()
        self.reset()

    def _bg(self):
        s = pygame.Surface((W, H))
        for y in range(0, H, 2):
            t = y / H
            col = (int(28 + 36 * math.sin(t * 2.4)), int(6 + 14 * t), int(32 + 48 * (1 - t)))
            pygame.draw.line(s, col, (0, y), (W, y + 1))
        return s

    def reset(self):
        self.t = 0
        self.score = 0
        self.combo = 1
        self.wi = 0
        self.prog = 0
        self.px = W / 2
        self.glyphs = []
        self.sparks = []
        self.banner = 0
        self.spawn = 0
        self.lives = 3
        random.seed(11)

    @property
    def word(self):
        return WORDS[self.wi % len(WORDS)]

    def need(self):
        w = self.word
        return w[self.prog] if self.prog < len(w) else None

    def spawn_glyph(self):
        lane = random.randrange(LANES)
        x = 130 + lane * (W - 260) / (LANES - 1)
        need = self.need()
        if need and random.random() < 0.5:
            ch = need
        else:
            ch = random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ")
        self.glyphs.append({"x": x + random.uniform(-8, 8), "y": 340, "ch": ch,
                            "vy": random.uniform(9.2, 13.4)})

    def step(self, keys=None, auto=False):
        self.t += 1
        self.banner = max(0, self.banner - 1)
        self.spawn -= 1
        if self.spawn <= 0:
            self.spawn_glyph()
            if self.t % 5 == 0:
                self.spawn_glyph()
            self.spawn = random.randint(7, 13)
        need = self.need()
        target = self.px
        if auto and need:
            cands = [g for g in self.glyphs if g["ch"] == need and 400 < g["y"] < 1560]
            if cands:
                cands.sort(key=lambda g: g["y"])
                target = cands[-1]["x"]
            else:
                target = W / 2 + math.sin(self.t * 0.07) * 280
        if keys:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.px -= 26
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.px += 26
        else:
            self.px += max(-24, min(24, target - self.px))
        self.px = max(120, min(W - 120, self.px))
        keep = []
        for g in self.glyphs:
            g["y"] += g["vy"]
            g["x"] += math.sin(self.t * 0.08 + g["y"] * 0.01) * 0.6
            hit = abs(g["x"] - self.px) < 86 and abs(g["y"] - 1588) < 40
            if hit:
                if need and g["ch"] == need:
                    self.prog += 1
                    self.score += 120 * self.combo
                    self.combo = min(9, self.combo + 1)
                    for i in range(16):
                        ang = i / 16 * math.tau
                        self.sparks.append([g["x"], g["y"], math.cos(ang) * 9, math.sin(ang) * 9, 16, GOLD])
                    if self.prog >= len(self.word):
                        self.score += 600
                        self.banner = 26
                        self.wi += 1
                        self.prog = 0
                else:
                    self.combo = 1
                    self.lives = max(1, self.lives - 1)
                    self.sparks.append([g["x"], g["y"], 0, -4, 12, VIO])
                continue
            if g["y"] < H + 50:
                keep.append(g)
        self.glyphs = keep[-18:]
        self.sparks = [s for s in self.sparks if s[4] > 0]
        for s in self.sparks:
            s[0] += s[2]
            s[1] += s[3]
            s[4] -= 1

    def draw(self, surf):
        surf.blit(self.bg, (0, 0))
        for i, col in enumerate((RASPB, TEAL, GOLD)):
            pts = [(x, 480 + i * 210 + math.sin(x * 0.012 + self.t * 0.05 + i) * 64) for x in range(0, W, 28)]
            pygame.draw.lines(surf, col, False, pts, 5)
        word = self.word
        gap = 86
        ox = W / 2 - (len(word) - 1) * gap / 2
        for i, ch in enumerate(word):
            filled = i < self.prog
            rect = pygame.Rect(0, 0, 74, 88)
            rect.center = (ox + i * gap, 268)
            pygame.draw.rect(surf, (48, 10, 32), rect, border_radius=14)
            pygame.draw.rect(surf, GOLD if filled else RASPB, rect, 4, border_radius=14)
            lab = self.mid.render(ch if filled else "?", True, GOLD if filled else MIST)
            surf.blit(lab, lab.get_rect(center=rect.center))
        need = self.need()
        for g in self.glyphs:
            hot = g["ch"] == need
            col = GOLD if hot else TEAL
            x, y = g["x"], g["y"]
            pygame.draw.polygon(surf, (40, 8, 28), [(x, y - 40), (x + 34, y), (x, y + 40), (x - 34, y)])
            pygame.draw.polygon(surf, col, [(x, y - 40), (x + 34, y), (x, y + 40), (x - 34, y)], 3)
            lab = self.mid.render(g["ch"], True, col)
            surf.blit(lab, lab.get_rect(center=(x, y)))
        px, py = self.px, 1588
        hull = [(px - 100, py), (px - 54, py - 40), (px + 54, py - 40), (px + 100, py),
                (px + 54, py + 32), (px - 54, py + 32)]
        pygame.draw.polygon(surf, (90, 16, 48), hull)
        pygame.draw.polygon(surf, RASPB, hull, 4)
        pygame.draw.circle(surf, GOLD, (int(px), int(py)), 16)
        for s in self.sparks:
            pygame.draw.circle(surf, s[5], (int(s[0]), int(s[1])), max(2, s[4] // 3))
        title = self.big.render("PEZZOTTAITE PHRASE", True, MIST)
        surf.blit(title, title.get_rect(center=(W // 2, 108)))
        sc = self.mid.render(f"SCORE  {self.score}", True, GOLD)
        surf.blit(sc, sc.get_rect(center=(W // 2, 176)))
        lives = self.tiny.render(f"SHARDS  {self.lives}    COMBO x{self.combo}", True, TEAL)
        surf.blit(lives, lives.get_rect(center=(W // 2, 340)))
        hint = self.tiny.render("catch the next glyph", True, (255, 176, 206))
        surf.blit(hint, hint.get_rect(center=(W // 2, H - 146)))
        tag = self.small.render("x.com/ElbowOS", True, TEAL)
        surf.blit(tag, tag.get_rect(center=(W // 2, H - 78)))
        if self.banner:
            b = self.big.render("PHRASE LOCK", True, GOLD)
            surf.blit(b, b.get_rect(center=(W // 2, 920)))

    def record(self):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "pipe:0", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-crf", "20", "-preset", "veryfast", "-movflags", "+faststart", OUT]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            for _ in range(FPS * SECS):
                self.step(auto=True)
                self.draw(self.screen)
                proc.stdin.write(pygame.image.tobytes(self.screen, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1500:]}")
        if os.path.abspath(OUT) != os.path.abspath(ALT):
            shutil.copy2(OUT, ALT)
        print("wrote", OUT, os.path.getsize(OUT))
        pygame.quit()

    def play(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                    self.reset()
            self.step(keys=pygame.key.get_pressed(), auto=False)
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()


def main():
    g = Game()
    g.play() if PLAY and not RECORD else g.record()


if __name__ == "__main__":
    main()
