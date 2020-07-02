import json
import random


class LoveTheoryAgent:
    def __init__(self, i, p, c):
        self.intimacy_points = i
        self.passion_points = p
        self.commitment_points = c
        self.working_memory = set()
        self.rules = set()
        self.fired_rules = set()
        self.goal = None
        self.subgoals = set()

    def set_rules(self, rules):
        self.rules = rules

    def reset_working_memory(self):
        self.working_memory = set()

    def forward_chaining(self):
        self.reset_working_memory()
        while True:
            has_fired_rules = False
            for rule in self.rules:
                if rule.fire(self.working_memory).issubset(self.working_memory):
                    continue
                has_fired_rules = True
                self.working_memory = self.working_memory.union(
                    rule.fire(self.working_memory))
                self.fired_rules.add((rule.id, rule.description))
            if not has_fired_rules:
                break
        return self.fired_rules

    def backward_chaining(self, goal):
        self.reset_working_memory()
        goals = set(goal)
        while len(goals) >= 1:
            for rule in self.rules:
                if rule.consequences == goals[-1]:
                    if len(rule.fire(self.working_memory)) == 0:
                        goals = goals.union(rule.antecedents)
                    else:
                        self.working_memory = self.working_memory.union(
                            rule.fire(self.working_memory))
                        goals = goals.difference(rule.consequences)
                        self.fired_rules.add((rule.id, rule.description))


class LoveTheoryRule:
    rule_count = 0

    def __init__(self, a, c, d, p=lambda x, y: x.issubset(y)):
        LoveTheoryRule.rule_count += 1
        self.id = LoveTheoryRule.rule_count
        self.antecedents = a
        self.consequences = c
        self.description = d
        self.predicate = p

    def fire(self, memory):
        if self.predicate(self.antecedents, memory):
            return self.consequences
        return set()


class LoveScale:
    def __init__(self, category, item):
        self.category = category
        self.item = item


if __name__ == "__main__":
    with open('love_scale.json') as scale:
        love_scale_dict = json.load(scale)

    with open('love_types.json') as types:
        love_types_dict = json.load(types)

    love_scale = []
    love_points = {'intimacy': 0, 'passion': 0, 'commitment': 0}
    rating_min = 1
    rating_max = 5

    for category in love_scale_dict:
        for item in love_scale_dict[category]['items']:
            love_scale.append(LoveScale(category, item))

    # random.shuffle(love_scale)
    print ("Please rate the following statements on a scale of 1 to 5 (1 = Strongly Disagree, 5 = Strong Agree)")
    for l in love_scale:
        print(l.item)
        user_in = input()
        rating = int(user_in)
        while not (rating >= rating_min and rating <= rating_max):
            print("Invalid input. Please enter an integer number between 1 and 5.")
            user_in = input()
            rating = int(user_in)
        love_points[l.category] += rating

    agent = LoveTheoryAgent(
        love_points['intimacy'], love_points['passion'], love_points['commitment'])
    rules = {
        LoveTheoryRule(agent.intimacy_points, {"intimacy"}, "If intimacy_points > (total_points / 2), then intimacy.",
                       lambda x, y: x >= (rating_max + rating_min) / 2 * len([l for l in love_scale if l.category == 'intimacy'])),
        LoveTheoryRule(agent.passion_points, {"passion"}, "If passion_points > (total_points / 2), then passion.",
                       lambda x, y: x >= (rating_max + rating_min) / 2 * len([l for l in love_scale if l.category == 'passion'])),
        LoveTheoryRule(agent.commitment_points, {"commitment"}, "If commitment_points > (total_points / 2), then commitment.",
                       lambda x, y: x >= (rating_max + rating_min) / 2 * len([l for l in love_scale if l.category == 'commitment']))
    }

    agent.set_rules(rules)
    fired_rules = agent.forward_chaining()

    for f in fired_rules:
        print(f)
