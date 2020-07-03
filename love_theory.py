import json
import random


class LoveTheoryAgent:
    def __init__(self, i, p, c):
        self.intimacy_points = i
        self.passion_points = p
        self.commitment_points = c
        self.working_memory = set()
        self.initialization_rules = set()
        self.production_rules = set()

    def set_initialization_rules(self, rules):
        self.initialization_rules = rules

    def set_production_rules(self, rules):
        self.production_rules = rules

    def initialize_working_memory(self):
        for rule in self.initialization_rules:
            self.working_memory = self.working_memory.union(rule.fire())

    def forward_chaining(self):
        self.initialize_working_memory()
        fired_rules = []
        while True:
            has_fired_rules = False
            for rule in self.production_rules:
                if rule.fire(self.working_memory).issubset(self.working_memory):
                    continue
                has_fired_rules = True
                self.working_memory = self.working_memory.union(
                    rule.fire(self.working_memory))
                fired_rules.append((rule.id, rule.description))
            if not has_fired_rules:
                break
        return fired_rules

    def backward_chaining(self, goal):
        self.initialize_working_memory()
        goals = [goal]
        fired_rules = []
        while len(goals) >= 1:
            has_modified_goal = False
            for rule in self.production_rules:
                if goals[-1] in list(rule.consequences):
                    if len(rule.fire(self.working_memory)) == 0:
                        goals.extend(
                            [r for r in rule.antecedents if r not in list(self.working_memory)])
                    else:
                        for c in rule.consequences:
                            goals.remove(c)
                        self.working_memory = self.working_memory.union(
                            rule.fire(self.working_memory))
                        fired_rules.append((rule.id, rule.description))
                    has_modified_goal = True
                    break
            if not has_modified_goal:
                break
        unsatisfied_antecedents = []
        if len(goals) >= 1:
            subgoals = set(goals[1:])
            antecedents = set()
            for rule in self.initialization_rules:
                antecedents = antecedents.union(rule.consequences)
            unsatisfied_antecedents = list(antecedents.intersection(subgoals))

        return (fired_rules, unsatisfied_antecedents)


class LoveTheoryRule:
    rule_count = 0

    def __init__(self, a, c, d, p):
        LoveTheoryRule.rule_count += 1
        self.id = LoveTheoryRule.rule_count
        self.antecedents = a
        self.consequences = c
        self.description = d
        self.predicate = p

    def fire(self, memory=set()):
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
    
    print("Hi, welcome to our system. Please select the types of chaining. (1 = Forward Chaining, 2 = Backward Chaining")
    while True:
            try:
                # Select types of chaining 
                method = int(input())
                if (method == 1 or method == 2):
                    break
            except ValueError:
                pass

            print("Invalid input. Please enter an integer number between 1 and 2.")

    # random.shuffle(love_scale)
    print(f"Please rate the following statements on a scale of {rating_min} to {rating_max} ({rating_min} = Strongly Disagree, {rating_max} = Strongly Agree)")
    for l in love_scale:
        print(l.item)
        while True: 
            try:
                rating = int(input())
                if (rating >= rating_min and rating <= rating_max):
                    break
                    
            except ValueError:
                pass      

            print("Invalid input. Please enter an integer number between 1 and 5.")        

        love_points[l.category] += rating
    
    agent = LoveTheoryAgent(
        love_points['intimacy'], love_points['passion'], love_points['commitment'])

    initialization = {
        LoveTheoryRule(agent.intimacy_points, {"intimacy"}, "If intimacy_points > (total_points / 2), then intimacy.",
                       lambda x, _: x >= (rating_max + rating_min) / 2 * len([l for l in love_scale if l.category == 'intimacy'])),
        LoveTheoryRule(agent.passion_points, {"passion"}, "If passion_points > (total_points / 2), then passion.",
                       lambda x, _: x >= (rating_max + rating_min) / 2 * len([l for l in love_scale if l.category == 'passion'])),
        LoveTheoryRule(agent.commitment_points, {"commitment"}, "If commitment_points > (total_points / 2), then commitment.",
                       lambda x, _: x >= (rating_max + rating_min) / 2 * len([l for l in love_scale if l.category == 'commitment']))
    }

    agent.set_initialization_rules(initialization)

    production = {
        LoveTheoryRule(set(), {"nonlove"}, "If intimacy, passion, commitment are all absent, then nonlove.",
                       lambda _, y: not ("intimacy" in y or "passion" in y or "commitment" in y)),
        LoveTheoryRule({"intimacy"}, {"friendship"}, "If intimacy, then friendship.",
                       lambda x, y: x == y),
        LoveTheoryRule({"passion"}, {"infatuation"}, "If passion, then infatuation.",
                       lambda x, y: x == y),
        LoveTheoryRule({"commitment"}, {"empty love"}, "If commitment, then empty love.",
                       lambda x, y: x == y),
        LoveTheoryRule({"intimacy", "passion"}, {"romantic love"}, "If intimacy and passion, then romantic love.",
                       lambda x, y: x == y),
        LoveTheoryRule({"intimacy", "commitment"}, {"companionate love"}, "If intimacy and commitment, then companionate love.",
                       lambda x, y: x == y),
        LoveTheoryRule({"commitment", "passion"}, {"fatuous love"}, "If commitment and passion, then fatuous love.",
                       lambda x, y: x == y),
        LoveTheoryRule({"intimacy", "commitment", "passion"}, {"consummate love"}, "If intimacy, commitment and passion, then consummate love.",
                       lambda x, y: x == y)
    }

    agent.set_production_rules(production)

    # LoveTheoryRule({"nonlove"}, {"nonlove description"}, "If nonlove, then nonlove description."),
    # LoveTheoryRule({"friendship"}, {"friendship description"}, "If friendship, then friendship description."),
    # LoveTheoryRule({"infatuation"}, {"infatuation description"}, "If infatuation, then infatuation description."),
    # LoveTheoryRule({"empty love"}, {"empty love description"}, "If empty love, then empty love description."),
    # LoveTheoryRule({"romantic love"}, {"romantic love description"}, "If romantic love, then romantic love description."),
    # LoveTheoryRule({"companionate love"}, {"companionate love description"}, "If companionate love, then companionate love description."),
    # LoveTheoryRule({"fatuous love"}, {"fatuous love description"}, "If fatuous love, then fatuous love description."),
    # LoveTheoryRule({"consummate love"}, {"consummate love description"}, "If consummate love, then consummate love description.")

    # Forward Chaining
    if (method == 1):
        fired_rules = agent.forward_chaining()
    else:
        fired_rules, unsatisfied_antecedents = agent.backward_chaining(
            "consummate love")
        for u in unsatisfied_antecedents:
            print(u)

    for f in fired_rules:
        print(f)

    
        
