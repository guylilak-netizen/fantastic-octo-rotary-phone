"""
life.py
A small, importable Life class adapted from the earlier single-file simulator.
Provides to_dict() and a tick_with_choice(choice) to allow deterministic choices.
"""

import random
from typing import Optional, List, Tuple

class Life:
    def __init__(self, name: str = "Player", seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.name = name
        self.age = 0
        self.alive = True
        self.happiness = 50
        self.health = 50
        self.smarts = 50
        self.looks = 50
        self.money = 1000
        self.married = False
        self.children = 0
        self.career = None
        self.history: List[Tuple[int, str]] = []

    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "alive": self.alive,
            "happiness": self.happiness,
            "health": self.health,
            "smarts": self.smarts,
            "looks": self.looks,
            "money": self.money,
            "married": self.married,
            "children": self.children,
            "career": self.career,
            "history": self.history,
        }

    def tick_with_choice(self, choice: Optional[str] = None) -> str:
        """
        Advance one year. If a choice is provided, apply its deterministic effects first.
        Returns a short description of the year's notable event(s).
        """
        if not self.alive:
            return "Already deceased."

        self.age += 1

        # Apply explicit choice effects
        choice_desc = ""
        if choice:
            c = choice.lower()
            if c == "work":
                income = random.randint(500, 8000) if self.career else random.randint(200, 2000)
                self.money += income
                self.happiness += random.randint(-2, 2)
                self.health += random.randint(-1, 1)
                choice_desc = f"Chose to work and earned ${income}."
            elif c == "study":
                self.smarts += random.randint(1, 4)
                self.happiness -= 1
                choice_desc = "Chose to study and improved smarts."
            elif c == "exercise":
                self.health += random.randint(1, 4)
                self.happiness += 1
                choice_desc = "Chose to exercise and improved health."
            elif c == "party":
                self.happiness += random.randint(1, 8)
                self.health -= random.randint(0, 3)
                self.money -= random.randint(0, 200)
                choice_desc = "Chose to party."
            elif c == "risk":
                # take a risky action (e.g., start business / crime)
                if random.random() < 0.25:
                    gain = random.randint(1000, 50000)
                    self.money += gain
                    self.happiness += 8
                    choice_desc = f"Took a risk and it paid off: +${gain}."
                else:
                    loss = random.randint(100, 20000)
                    self.money -= loss
                    self.happiness -= 6
                    choice_desc = f"Took a risk and lost ${loss}."
            else:
                choice_desc = "Made a quiet choice."

        # Now a mostly-random event occurs (smaller than before)
        event = self.random_event(small=True)

        # apply aging decay
        self.random_decay()
        self.check_death()

        desc = ", ".join([d for d in [choice_desc, event] if d])
        if not desc:
            desc = "A quiet year passed."

        self.history.append((self.age, desc))
        return desc

    def random_event(self, small: bool = False) -> str:
        # Simple weighted events
        events = ["nothing"] * 6
        events += ["lottery"] * (1 if not small else 0)
        events += ["meet_partner"] * 2
        events += ["health_issue"] * (2 if not small else 1)
        events += ["have_child"] * 1
        events += ["find_job"] * (2 if self.age >= 18 and not self.career else 1)
        events += ["start_business"] * (1 if not small else 0)

        choice = random.choice(events)

        if choice == "nothing":
            return "Nothing special happened."
        if choice == "lottery":
            if random.random() < 0.01:
                win = random.randint(50000, 500000)
                self.money += win
                self.happiness += 10
                return f"Won the lottery: ${win}!"
            else:
                self.money -= 10
                return "Bought a lottery ticket and lost."
        if choice == "meet_partner":
            if not self.married and random.random() < 0.5:
                self.married = True
                self.happiness += 8
                return "Met a partner and got married."
            return "Met new people."
        if choice == "health_issue":
            loss = random.randint(3, 25)
            self.health -= loss
            self.happiness -= random.randint(1, 4)
            return f"Suffered a health issue and lost {loss} health."
        if choice == "have_child":
            if self.age >= 18 and random.random() < 0.4:
                self.children += 1
                self.happiness += 6
                self.money -= random.randint(500, 15000)
                return "Had a child."
            return "No childbirth this year."
        if choice == "find_job":
            if not self.career and random.random() < 0.6:
                self.career = random.choice(["Retail", "Office", "Engineer", "Doctor", "Artist", "Entrepreneur"])
                self.money += 500
                self.happiness += 2
                self.smarts += 1
                return f"Found a job as {self.career}."
            return "Job search continues."
        if choice == "start_business":
            success = random.random() < 0.2
            investment = random.randint(1000, 30000)
            self.money -= investment
            if success:
                gain = investment * random.randint(2, 8)
                self.money += gain
                self.happiness += 12
                return f"Started a business and it paid off: +${gain}."
            else:
                self.happiness -= 5
                return f"Started a business that failed, lost ${investment}."
        return "An uneventful year."

    def random_decay(self):
        if self.age > 30:
            self.health -= int((self.age - 30) * 0.25)
        self.happiness += random.randint(-2, 2)
        self.smarts += random.randint(0, 1)
        # clamp
        self.happiness = max(0, min(100, self.happiness))
        self.health = max(0, min(100, self.health))
        self.smarts = max(0, min(100, self.smarts))

    def check_death(self):
        if self.health <= 0:
            self.alive = False
            return
        base_death_chance = 0.001 * max(0, self.age - 40)
        health_modifier = (100 - self.health) / 1000.0
        if random.random() < (base_death_chance + health_modifier):
            self.alive = False

