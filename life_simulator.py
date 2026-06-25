"""
life_simulator.py
A tiny, self-contained BitLife-like life simulator.
Run: python3 life_simulator.py

Controls:
 - In interactive mode you press Enter each year to progress.
 - Use --auto to simulate until death/100.

This file is intentionally simple and has no external dependencies.
"""

import random
import argparse
import sys

class Life:
    def __init__(self, name="Player", seed=None):
        if seed is not None:
            random.seed(seed)
        self.name = name
        self.age = 0
        self.alive = True
        # Stats 0-100
        self.happiness = 50
        self.health = 50
        self.smarts = 50
        self.looks = 50
        self.money = 1000
        self.married = False
        self.children = 0
        self.career = None
        self.history = []

    def year_tick(self):
        if not self.alive:
            return
        self.age += 1
        event = self.choose_event()
        self.apply_event(event)
        self.random_decay()
        self.check_death()
        self.history.append((self.age, event))

    def choose_event(self):
        # Weighted list of events; some depend on age
        events = []
        # Common yearly events
        events.extend(["work"] * 8)
        events.extend(["study"] * 3)
        events.extend(["party"] * 3)
        events.extend(["exercise"] * 4)
        events.extend(["junk_food"] * 3)
        events.extend(["health_issue"] * 2)
        events.extend(["lottery"] * 1)
        events.extend(["start_business"] * 1)
        events.extend(["crime"] * 1)

        if 18 <= self.age <= 26:
            events.extend(["college"] * 4)
        if self.age >= 20 and self.career is None:
            events.extend(["find_job"] * 6)
        if 22 <= self.age <= 45:
            events.extend(["meet_partner"] * 3)
            events.extend(["have_child"] * 2)
        if self.married and random.random() < 0.02:
            events.append("divorce")
        # pick
        return random.choice(events)

    def apply_event(self, event):
        # Effects on stats
        if event == "work":
            income = random.randint(1000, 10000) if self.career else random.randint(200, 2000)
            self.money += income
            self.happiness += random.randint(-3, 3)
            self.health += random.randint(-2, 1)
            if self.career and random.random() < 0.05:
                self.happiness += 5  # promotion
                self.money += 5000
            desc = f"Worked and earned ${income}."

        elif event == "find_job":
            self.career = random.choice(["Retail", "Office", "Engineer", "Doctor", "Artist", "Entrepreneur"])
            self.money += 500
            self.happiness += 3
            self.smarts += 1
            desc = f"Found a job as {self.career}."

        elif event == "college":
            cost = random.randint(5000, 50000)
            self.money -= cost
            self.smarts += random.randint(3, 10)
            self.happiness += 2
            desc = f"Attended college and spent ${cost}."

        elif event == "study":
            self.smarts += random.randint(1, 3)
            self.happiness -= 1
            desc = "Studied and improved smarts."

        elif event == "exercise":
            self.health += random.randint(1, 4)
            self.happiness += 1
            desc = "Exercised and improved health."

        elif event == "junk_food":
            self.health -= random.randint(1, 4)
            self.happiness += random.randint(0, 3)
            desc = "Ate junk food."

        elif event == "party":
            self.happiness += random.randint(1, 8)
            self.health -= random.randint(0, 3)
            self.money -= random.randint(0, 200)
            desc = "Partied."

        elif event == "health_issue":
            loss = random.randint(5, 30)
            self.health -= loss
            self.happiness -= random.randint(1, 5)
            desc = f"Suffered a health issue and lost {loss} health."

        elif event == "lottery":
            if random.random() < 0.01:
                win = random.randint(50000, 500000)
                self.money += win
                self.happiness += 10
                desc = f"Won the lottery: ${win}!"
            else:
                self.money -= 10
                desc = "Bought a lottery ticket and lost."

        elif event == "start_business":
            success = random.random() < 0.2
            investment = random.randint(1000, 50000)
            self.money -= investment
            if success:
                gain = investment * random.randint(2, 10)
                self.money += gain
                self.happiness += 10
                desc = f"Started a business and it paid off: +${gain}."
            else:
                self.happiness -= 5
                desc = f"Started a business that failed, lost ${investment}."

        elif event == "crime":
            if random.random() < 0.3:
                fine = random.randint(100, 5000)
                self.money -= fine
                self.happiness -= 5
                desc = f"Got in trouble with the law and paid ${fine}."
            else:
                gain = random.randint(100, 3000)
                self.money += gain
                self.happiness -= 10
                desc = f"Committed a crime and gained ${gain} (at moral cost)."

        elif event == "meet_partner":
            if not self.married and random.random() < 0.5:
                self.married = True
                self.happiness += 10
                desc = "Met a partner and got married."
            else:
                self.happiness += 2
                desc = "Met new people."

        elif event == "have_child":
            if self.age >= 18 and random.random() < 0.4:
                self.children += 1
                self.happiness += 8
                self.money -= random.randint(1000, 20000)
                desc = "Had a child."
            else:
                desc = "Childbirth didn't happen this year."

        elif event == "divorce":
            if self.married:
                self.married = False
                self.happiness -= 15
                self.money -= random.randint(1000, 50000)
                desc = "Divorced."
            else:
                desc = "No change."

        else:
            desc = "A quiet year passed."

        # clamp stats 0-100
        self.happiness = max(0, min(100, self.happiness))
        self.health = max(0, min(100, self.health))
        self.smarts = max(0, min(100, self.smarts))
        self.looks = max(0, min(100, self.looks))
        if self.money < 0:
            # negative money allowed, but not too negative
            self.money = max(self.money, -1000000)

        return desc

    def random_decay(self):
        # Aging effects
        if self.age > 30:
            self.health -= int((self.age - 30) * 0.3)
        # small yearly randomness
        self.happiness += random.randint(-2, 2)
        self.smarts += random.randint(0, 1)
        # clamp again
        self.happiness = max(0, min(100, self.happiness))
        self.smarts = max(0, min(100, self.smarts))

    def check_death(self):
        # death from low health
        if self.health <= 0:
            self.alive = False
            return
        # age-related mortality
        base_death_chance = 0.001 * max(0, self.age - 40)
        # higher if low health
        health_modifier = (100 - self.health) / 1000.0
        roll = random.random()
        if roll < (base_death_chance + health_modifier):
            self.alive = False

    def summary(self):
        return (
            f"Name: {self.name}\n"
            f"Age: {self.age} {'(alive)' if self.alive else '(deceased)'}\n"
            f"Money: ${self.money}\n"
            f"Health: {self.health}\n"
            f"Happiness: {self.happiness}\n"
            f"Smarts: {self.smarts}\n"
            f"Looks: {self.looks}\n"
            f"Married: {self.married}\n"
            f"Children: {self.children}\n"
            f"Career: {self.career}\n"
        )


def run_simulation(interactive=True, years=None, seed=None, name="Player"):
    life = Life(name=name, seed=seed)
    if years is None:
        max_years = 100
    else:
        max_years = years

    while life.alive and life.age < max_years:
        life.year_tick()
        event = life.history[-1][1]
        if interactive:
            print(f"Year {life.age}: {event}")
            print(life.summary())
            inp = input("Press Enter to continue, or type 'q' to quit: ")
            if inp.strip().lower() == 'q':
                break
        else:
            # in auto mode, minimal printing
            pass

    print("\nFinal summary:")
    print(life.summary())
    print("History (last 10 years):")
    for age, ev in life.history[-10:]:
        print(f"  Age {age}: {ev}")
    return life


def main(argv):
    parser = argparse.ArgumentParser(description='Simple BitLife-like simulator')
    parser.add_argument('--auto', action='store_true', help='Run non-interactive full simulation')
    parser.add_argument('--years', type=int, default=None, help='Stop after N years (overrides default 100)')
    parser.add_argument('--seed', type=int, default=None, help='Random seed (integer)')
    parser.add_argument('--name', type=str, default='Player', help='Name of the character')
    args = parser.parse_args(argv)

    if args.auto:
        run_simulation(interactive=False, years=args.years or 100, seed=args.seed, name=args.name)
    else:
        try:
            run_simulation(interactive=True, years=args.years or 100, seed=args.seed, name=args.name)
        except KeyboardInterrupt:
            print('\nSimulation interrupted.')


if __name__ == '__main__':
    main(sys.argv[1:])
