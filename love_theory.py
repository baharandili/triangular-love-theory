import json
import random
import copy

class LoveTheoryAgent:
    def __init__(self, *, intimacy_points, passion_points, commitment_points):
        self.intimacy_points = intimacy_points
        self.passion_points = passion_points
        self.commitment_points = commitment_points
        self.working_memory = set()
        self.initialization_rules = set()
        self.production_rules = set()
        self.correction_rules = set()

    def set_rules(self, *, initialization, production, correction):
        self.initialization_rules = initialization
        self.production_rules = production
        self.correction_rules = correction

    def __initialize_working_memory(self):
        for rule in self.initialization_rules:
            self.working_memory = self.working_memory.union(rule.fire())
    
    def __get_rule(self, r):
        matching_rule = None 
        all_rules = self.initialization_rules.union(self.production_rules.union(self.correction_rules))
        for rule in list(all_rules):
            if rule.id == r:
                matching_rule = rule
                break
        return matching_rule

    def forward_chaining(self):
        self.__initialize_working_memory()
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
        # TODO: Should return the final decision here 
        return fired_rules
        

    def backward_chaining(self, goal):
        self.__initialize_working_memory()
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
        else: 
            tracer = copy.deepcopy(self.working_memory)
            for f in fired_rules:
                tracer = tracer.difference(self.__get_rule(f[0]).antecedents)
            if len(tracer) > 1:
                for rule in self.correction_rules:
                    if not rule.fire(tracer).issubset(tracer):
                        tracer = tracer.union(rule.fire(tracer))
                        fired_rules.append((rule.id, rule.description))
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

    # random.shuffle(love_scale)
    print(f"Please rate the following statements on a scale of {rating_min} to {rating_max} \
        ({rating_min} = Strongly Disagree, {rating_max} = Strong Agree)")
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
        intimacy_points=love_points['intimacy'], passion_points=love_points['passion'], commitment_points=love_points['commitment'])

    initialization = {
        LoveTheoryRule(agent.intimacy_points, {"intimacy"}, "If intimacy_points > (total_points / 2), then intimacy.",
                       lambda x, _: x >= (rating_max + rating_min) / 2 * len([l for l in love_scale if l.category == 'intimacy'])),
        LoveTheoryRule(agent.passion_points, {"passion"}, "If passion_points > (total_points / 2), then passion.",
                       lambda x, _: x >= (rating_max + rating_min) / 2 * len([l for l in love_scale if l.category == 'passion'])),
        LoveTheoryRule(agent.commitment_points, {"commitment"}, "If commitment_points > (total_points / 2), then commitment.",
                       lambda x, _: x >= (rating_max + rating_min) / 2 * len([l for l in love_scale if l.category == 'commitment']))
    }

    production = {
        LoveTheoryRule(set(), {"nonlove"}, "If intimacy, passion, commitment are all absent, then nonlove.",
                       lambda _, y: not ("intimacy" in y or "passion" in y or "commitment" in y)),

        LoveTheoryRule({"intimacy"}, {"friendship"}, "If intimacy, then friendship.",
                       lambda x, y: x.issubset(y)),
        LoveTheoryRule({"passion"}, {"infatuation"}, "If passion, then infatuation.",
                       lambda x, y: x.issubset(y)),
        LoveTheoryRule({"commitment"}, {"empty love"}, "If commitment, then empty love.",
                       lambda x, y: x.issubset(y)),

        LoveTheoryRule({"intimacy", "passion"}, {"romantic love"}, "If intimacy and passion, then romantic love.",
                       lambda x, y: x.issubset(y)),
        LoveTheoryRule({"intimacy", "commitment"}, {"companionate love"}, "If intimacy and commitment, then companionate love.",
                       lambda x, y: x.issubset(y)),
        LoveTheoryRule({"commitment", "passion"}, {"fatuous love"}, "If commitment and passion, then fatuous love.",
                       lambda x, y: x.issubset(y)),

        LoveTheoryRule({"intimacy", "commitment", "passion"}, {"consummate love"}, "If intimacy, commitment and passion, then consummate love.",
                       lambda x, y: x.issubset(y))
    }

    correction = {
        LoveTheoryRule({"friendship", "passion"}, {"romantic love"}, "If friendship and passion, then romantic love.",
                       lambda x, y: x == y),
        LoveTheoryRule({"intimacy", "infatuation"}, {"romantic love"}, "If intimacy and infatuation, then romantic love.",
                       lambda x, y: x == y),

        LoveTheoryRule({"friendship", "commitment"}, {"companionate love"}, "If friendship and commitment, then companionate love.",
                       lambda x, y: x == y),
        LoveTheoryRule({"intimacy", "empty love"}, {"companionate love"}, "If intimacy and empty love, then companionate love.",
                       lambda x, y: x == y),

        LoveTheoryRule({"empty love", "passion"}, {"fatuous love"}, "If empty love and passion, then fatuous love.",
                       lambda x, y: x == y),
        LoveTheoryRule({"commitment", "infatuation"}, {"fatuous love"}, "If commitment and infatuation, then fatuous love.",
                       lambda x, y: x == y),

        LoveTheoryRule({"friendship", "commitment", "passion"}, {"consummate love"}, "If friendship, commitment and passion, then consummate love.",
                       lambda x, y: x == y),
        LoveTheoryRule({"intimacy", "empty love", "passion"}, {"consummate love"}, "If intimacy, empty love and passion, then consummate love.",
                       lambda x, y: x == y),
        LoveTheoryRule({"intimacy", "commitment", "infatuation"}, {"consummate love"}, "If intimacy, commitment and infatuation, then consummate love.",
                       lambda x, y: x == y),
        LoveTheoryRule({"romantic love", "commitment"}, {"consummate love"}, "If romantic love and commitment, then consummate love.",
                       lambda x, y: x == y),
        LoveTheoryRule({"companionate love", "passion"}, {"consummate love"}, "If companionate love and passion, then consummate love.",
                       lambda x, y: x == y),
        LoveTheoryRule({"fatuous love", "intimacy"}, {"consummate love"}, "If fatuous love and intimacy, then consummate love.",
                       lambda x, y: x == y)
    }

    agent.set_rules(initialization=initialization, production=production, correction=correction)

    fired_rules, unsatisfied_antecedents = agent.backward_chaining(
        "fatuous love")

    for f in fired_rules:
        print(f)

    for u in unsatisfied_antecedents:
        print(u)
