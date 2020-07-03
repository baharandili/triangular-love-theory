class LoveTheoryAgent:
    def __init__(self, *, intimacy_points, passion_points, commitment_points):
        self.intimacy_points = intimacy_points
        self.passion_points = passion_points
        self.commitment_points = commitment_points
        self.working_memory = set()
        self.initialization_rules = []
        self.production_rules = []
        self.correction_rules = []

    def set_rules(self, *, initialization, production, correction):
        self.initialization_rules = initialization
        self.production_rules = production
        self.correction_rules = correction

    def __initialize_working_memory(self):
        for rule in self.initialization_rules:
            self.working_memory = self.working_memory.union(rule.fire())

    def __get_rule(self, r):
        matching_rule = None
        all_rules = self.initialization_rules + \
            self.production_rules + self.correction_rules
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
                fired_rules.append((rule.id, rule.antecedents, rule.consequences))
            if not has_fired_rules:
                break
        return fired_rules

    def backward_chaining(self, goal):
        self.__initialize_working_memory()
        goals = list(goal)
        rule_log = {
            'fired': [],
            'corrected': []
        }
        while len(goals) >= 1:
            has_modified_goal = False
            for rule in self.production_rules:
                if goals[-1] in list(rule.consequences):
                    if len(rule.fire(self.working_memory)) == 0 and len(rule.antecedents) >= 1:
                        goals.extend(
                            [r for r in rule.antecedents if r not in list(self.working_memory)])
                        has_modified_goal = True
                    elif len(rule.fire(self.working_memory)) >= 1:
                        for c in rule.consequences:
                            goals.remove(c)
                        self.working_memory = self.working_memory.union(
                            rule.fire(self.working_memory))
                        rule_log['fired'].append((rule.id, rule.antecedents, rule.consequences))
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
            unused_antecedents = self.working_memory.copy()
            for f in rule_log['fired']:
                unused_antecedents = unused_antecedents.difference(
                    self.__get_rule(f[0]).antecedents)
            if len(unused_antecedents) > 1:
                for rule in self.correction_rules:
                    if not rule.fire(unused_antecedents).issubset(unused_antecedents):
                        unused_antecedents = unused_antecedents.union(
                            rule.fire(unused_antecedents))
                        rule_log['corrected'].append((rule.id, rule.antecedents, rule.consequences))
        return (rule_log, unsatisfied_antecedents)


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
