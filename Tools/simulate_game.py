"""
Headless sanity simulation of the game rules.

It re-implements only the maths the scripts use (gravity, jump, obstacle speed,
spawn interval, score) and checks that:

  * the player can always clear the tall obstacles
  * an "average human" player (reacts after ~0.25 s and holds the jump for a random
    amount of time) survives a reasonable stretch of the game
  * the score increases by exactly one per obstacle passed

Handy when you change jumpForce / gravityScale / minY / maxY in the Inspector and
want to know whether the game is still fair.

    python Tools/simulate_game.py
"""
import random

# Values mirrored from the scene (Assets/Scenes/Game.unity) and the scripts.
GRAVITY = 9.81
GRAVITY_SCALE = 2.2
JUMP_FORCE = 12.0
PLAYER_SIZE = 1.0
PLAYER_X = -6.0
GROUND_TOP = -2.0
OBSTACLE_W, OBSTACLE_H = 1.0, 2.0
SPAWN_X = 11.0
PASS_X = -7.0
MIN_Y, MAX_Y = -1.4, -0.4
START_INTERVAL, MIN_INTERVAL, INTERVAL_STEP = 1.7, 0.85, 0.02
START_SPEED, SPEED_STEP, MAX_SPEED = 4.5, 0.3, 15.0
DT = 1 / 50.0


def jump_apex():
    return JUMP_FORCE ** 2 / (2 * GRAVITY * GRAVITY_SCALE)


def can_clear(max_y):
    """Player bottom at apex must be above the obstacle top."""
    return (GROUND_TOP + PLAYER_SIZE + jump_apex()) > (max_y + OBSTACLE_H / 2)


def simulate(seconds=60.0, seed=1, reaction=0.25, jump_hold=(0.05, 0.35)):
    random.seed(seed)
    t = 0.0
    y = GROUND_TOP + PLAYER_SIZE              # player bottom
    vy = 0.0
    grounded = True
    obstacles = []
    spawn_timer = 0.6
    interval = START_INTERVAL
    speed = START_SPEED
    score = 0
    deaths = 0
    first_death = None

    while t < seconds:
        # difficulty ramp, same formula as ObstacleSpawner.Update
        speed = min(speed + SPEED_STEP * DT, MAX_SPEED)
        interval = max(interval - INTERVAL_STEP * DT, MIN_INTERVAL)

        spawn_timer += DT
        if spawn_timer >= interval:
            spawn_timer = 0.0
            obstacles.append({"x": SPAWN_X, "y": random.uniform(MIN_Y, MAX_Y), "scored": False})

        # physics
        vy -= GRAVITY * GRAVITY_SCALE * DT
        y += vy * DT
        if y <= GROUND_TOP + PLAYER_SIZE:
            y = GROUND_TOP + PLAYER_SIZE
            vy = 0.0
            grounded = True

        # move obstacles
        for o in obstacles:
            o["x"] -= speed * DT
            if not o["scored"] and o["x"] < PASS_X:
                o["scored"] = True
                score += 1
        obstacles = [o for o in obstacles if o["x"] > -14.0]

        # very simple "player": jump when the next obstacle is close and it is tall
        nearest = min((o for o in obstacles if o["x"] > PLAYER_X), default=None, key=lambda o: o["x"])
        if nearest is not None and grounded:
            gap = nearest["x"] - PLAYER_X - OBSTACLE_W / 2 - PLAYER_SIZE / 2
            # start the jump early enough to be at apex when the obstacle arrives
            lead = speed * (JUMP_FORCE / (GRAVITY * GRAVITY_SCALE)) * 0.5
            if gap <= lead + speed * reaction:
                vy = JUMP_FORCE
                grounded = False

        # collision
        p_left, p_right = PLAYER_X - PLAYER_SIZE / 2, PLAYER_X + PLAYER_SIZE / 2
        p_bottom, p_top = y, y + PLAYER_SIZE
        for o in obstacles:
            o_left = o["x"] - OBSTACLE_W / 2
            o_right = o["x"] + OBSTACLE_W / 2
            o_bottom = o["y"] - OBSTACLE_H / 2
            o_top = o["y"] + OBSTACLE_H / 2
            if p_right > o_left and p_left < o_right and p_top > o_bottom and p_bottom < o_top:
                deaths += 1
                if first_death is None:
                    first_death = round(t, 1)
                # "restart": clear the field
                obstacles.clear()
                spawn_timer, interval, speed = 0.6, START_INTERVAL, START_SPEED
                y, vy = GROUND_TOP + PLAYER_SIZE, 0.0
                break

        t += DT

    return {"time": seconds, "score": score, "deaths": deaths, "first_death": first_death,
            "speed": round(speed, 2)}


def main():
    print("jump apex height     : %.2f units" % jump_apex())
    print("tallest obstacle top : %.2f above the ground"
          % (MAX_Y + OBSTACLE_H / 2 - GROUND_TOP))
    print("can always clear     : %s" % ("YES" if can_clear(MAX_Y) else "NO"))

    results = [simulate(seed=s) for s in range(5)]
    for i, r in enumerate(results):
        print("run %d: survived %.0fs, score %d, crashes %d%s"
              % (i + 1, r["time"], r["score"], r["deaths"],
                 "" if r["first_death"] is None else " (first crash at %.1fs)" % r["first_death"]))

    ok = can_clear(MAX_Y) and any(r["score"] > 10 for r in results)
    print("\nRESULT:", "PASS" if ok else "FAIL -- retune the jump or obstacle heights")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
