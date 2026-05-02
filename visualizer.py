import sys
import pygame
from task import Task
from simulation import Simulation

def build_tasks():
     return [
        Task("SensorProc",   period=20,  execution_time=8,  deadline=20,  priority="critical"),
        Task("Perception",   period=50,  execution_time=13, deadline=50,  priority="critical"),
        Task("Localization", period=40,  execution_time=5,  deadline=40,  priority="high"),
        Task("Planning",     period=100, execution_time=6,  deadline=100, priority="high"),
        Task("Control",      period=20,  execution_time=3,  deadline=20,  priority="critical"),
        Task("SysMonitor",   period=200, execution_time=2,  deadline=200, priority="background"),
    ]

SIM_TIME = 300

rms_metrics = Simulation(build_tasks(), "RMS", sim_time=SIM_TIME).run()
edf_metrics = Simulation(build_tasks(), "EDF", sim_time=SIM_TIME).run()

TASK_NAMES = [t.name for t in build_tasks()]


BG          = (15,  17,  26)
PANEL_BG    = (22,  25,  38)
TEXT_COL    = (220, 220, 230)
DIM_TEXT    = (110, 115, 140)
ACCENT      = (82,  130, 255)
MISS_COL    = (255,  70,  70)
IDLE_COL    = (45,   48,  65)

PRIORITY_COLORS = {
    "critical":   (82,  200, 130),
    "high":       (82,  130, 255),
    "background": (180, 130, 255),
    "none":       IDLE_COL,
}

TASK_COLORS = {
    "SensorProc":   (82,  200, 130),
    "Perception":   (255, 180,  60),
    "Localization": (82,  130, 255),
    "Planning":     (200,  82, 200),
    "Control":      ( 60, 210, 230),
    "SysMonitor":   (160, 160, 180),
    "IDLE":         IDLE_COL,
}

W, H         = 1280, 720
ROW_H        = 36          # height of one Gantt row
LABEL_W      = 110         # left label column
CHART_LEFT   = LABEL_W + 10
CHART_RIGHT  = W - 20
CHART_W      = CHART_RIGHT - CHART_LEFT

GANTT_TOP_RMS = 110        # y-start of RMS gantt
GANTT_TOP_EDF = GANTT_TOP_RMS + (len(TASK_NAMES) + 2) * ROW_H + 50

TICK_SPEED   = 4           # pixels per ms tick at zoom=1
VISIBLE_MS   = CHART_W // TICK_SPEED  # how many ms fit on screen


def build_gantt(log):
    """
    Convert the event log into per-task run segments.
    Returns: dict  task_name -> list of (start_ms, end_ms, event_type)
    """
    gantt = {name: [] for name in TASK_NAMES}
    gantt["IDLE"] = []

    prev = None
    for entry in log:
        t   = entry["time"]
        name = entry["task"]
        evt  = entry["event"]

        if evt in ("run", "idle"):
            if prev and prev["task"] == name and prev["event"] == evt:
                # extend last segment
                key = name if name in gantt else "IDLE"
                if gantt[key]:
                    s, e, et = gantt[key][-1]
                    gantt[key][-1] = (s, t + 1, et)
            else:
                key = name if name in gantt else "IDLE"
                gantt[key].append((t, t + 1, evt))
        prev = entry

    return gantt


rms_gantt = build_gantt(rms_metrics["log"])
edf_gantt = build_gantt(edf_metrics["log"])


def ms_to_x(ms, scroll_offset):
    return CHART_LEFT + (ms - scroll_offset) * TICK_SPEED

# main visualization loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("AV Real-Time Scheduler — RMS vs EDF")
    clock  = pygame.time.Clock()

    font_sm  = pygame.font.SysFont("monospace", 12)
    font_md  = pygame.font.SysFont("monospace", 14, bold=True)
    font_lg  = pygame.font.SysFont("monospace", 18, bold=True)
    font_hdr = pygame.font.SysFont("monospace", 22, bold=True)

    playhead     = 0          # current ms being "played"
    scroll       = 0          # leftmost visible ms
    paused       = False
    play_timer   = 0.0        # sub-tick accumulator
    PLAY_SPEED   = 30         # ms of sim time per second of real time

    def draw_gantt(gantt, metrics, top_y, label):
        # Section header
        hdr = font_lg.render(f"▶ {label}   "
                             f"Misses: {metrics['deadline_misses']}  "
                             f"Miss Rate: {metrics['miss_rate']*100:.1f}%  "
                             f"Avg RT: {metrics['avg_response_time']} ms  "
                             f"CPU: {metrics['cpu_utilization']*100:.1f}%",
                             True, ACCENT)
        screen.blit(hdr, (10, top_y - 26))

        for i, name in enumerate(TASK_NAMES):
            row_y = top_y + i * ROW_H
            # Row background
            pygame.draw.rect(screen, PANEL_BG, (CHART_LEFT, row_y, CHART_W, ROW_H - 2))

            # Task label
            lbl = font_sm.render(name, True, TEXT_COL)
            screen.blit(lbl, (5, row_y + ROW_H // 2 - 6))

            # Segments
            color = TASK_COLORS.get(name, ACCENT)
            segments = gantt.get(name, [])
            for (s, e, evt) in segments:
                x1 = ms_to_x(s, scroll)
                x2 = ms_to_x(e, scroll)
                if x2 < CHART_LEFT or x1 > CHART_RIGHT:
                    continue
                x1 = max(x1, CHART_LEFT)
                x2 = min(x2, CHART_RIGHT)
                c = MISS_COL if evt == "miss" else color
                pygame.draw.rect(screen, c, (x1, row_y + 3, max(1, x2 - x1), ROW_H - 8))

        # IDLE row
        idle_y = top_y + len(TASK_NAMES) * ROW_H
        lbl = font_sm.render("IDLE", True, DIM_TEXT)
        screen.blit(lbl, (5, idle_y + ROW_H // 2 - 6))
        pygame.draw.rect(screen, PANEL_BG, (CHART_LEFT, idle_y, CHART_W, ROW_H - 2))
        for (s, e, _) in gantt.get("IDLE", []):
            x1 = ms_to_x(s, scroll)
            x2 = ms_to_x(e, scroll)
            if x2 < CHART_LEFT or x1 > CHART_RIGHT:
                continue
            x1 = max(x1, CHART_LEFT)
            x2 = min(x2, CHART_RIGHT)
            pygame.draw.rect(screen, IDLE_COL, (x1, idle_y + 3, max(1, x2 - x1), ROW_H - 8))

    def draw_timeline(top_y, rows):
        """Tick marks and ms labels across the bottom of a gantt."""
        axis_y = top_y + rows * ROW_H + 4
        pygame.draw.line(screen, DIM_TEXT, (CHART_LEFT, axis_y), (CHART_RIGHT, axis_y))
        step = 20 if TICK_SPEED >= 4 else 50
        for ms in range(0, SIM_TIME + 1, step):
            x = ms_to_x(ms, scroll)
            if CHART_LEFT <= x <= CHART_RIGHT:
                pygame.draw.line(screen, DIM_TEXT, (x, axis_y), (x, axis_y + 5))
                lbl = font_sm.render(str(ms), True, DIM_TEXT)
                screen.blit(lbl, (x - 8, axis_y + 7))

    def draw_playhead():
        px = ms_to_x(playhead, scroll)
        if CHART_LEFT <= px <= CHART_RIGHT:
            pygame.draw.line(screen, (255, 255, 100), (px, 80), (px, H - 30), 2)

    def draw_legend():
        x = CHART_LEFT
        for name, color in TASK_COLORS.items():
            if name == "IDLE":
                continue
            box = pygame.Rect(x, H - 22, 12, 12)
            pygame.draw.rect(screen, color, box)
            lbl = font_sm.render(name, True, TEXT_COL)
            screen.blit(lbl, (x + 16, H - 22))
            x += len(name) * 8 + 30
        # Miss color
        pygame.draw.rect(screen, MISS_COL, (x, H - 22, 12, 12))
        screen.blit(font_sm.render("DEADLINE MISS", True, MISS_COL), (x + 16, H - 22))

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_RIGHT and paused:
                    playhead = min(SIM_TIME, playhead + 1)
                elif event.key == pygame.K_LEFT and paused:
                    playhead = max(0, playhead - 1)

        # Advance playhead
        if not paused and playhead < SIM_TIME:
            play_timer += PLAY_SPEED * dt
            steps = int(play_timer)
            play_timer -= steps
            playhead = min(SIM_TIME, playhead + steps)

        # Auto-scroll to keep playhead visible
        visible_end = scroll + VISIBLE_MS
        if playhead > visible_end - 5:
            scroll = max(0, playhead - VISIBLE_MS + 5)
        if playhead < scroll + 5:
            scroll = max(0, playhead - 5)

        # Draw
        screen.fill(BG)

        # Title
        title = font_hdr.render("Autonomous Vehicle Real-Time Scheduler Simulation — RMS vs EDF", True, TEXT_COL)
        screen.blit(title, (10, 10))
        sub = font_sm.render(
            f"Time: {playhead} ms / {SIM_TIME} ms    [SPACE=pause  ←→=step  Q=quit]",
            True, DIM_TEXT)
        screen.blit(sub, (10, 38))

        draw_gantt(rms_gantt, rms_metrics, GANTT_TOP_RMS, "RMS (Rate Monotonic Scheduling)")
        draw_timeline(GANTT_TOP_RMS, len(TASK_NAMES) + 1)

        draw_gantt(edf_gantt, edf_metrics, GANTT_TOP_EDF, "EDF (Earliest Deadline First)")
        draw_timeline(GANTT_TOP_EDF, len(TASK_NAMES) + 1)

        draw_playhead()
        draw_legend()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
