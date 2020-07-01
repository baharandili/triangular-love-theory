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
        has_fired_rules = False
        while True:
            for rule in self.rules:
                if rule.fire(self.working_memory) in self.working_memory or len(rule.fire(self.working_memory)) == 0:
                    continue
                has_fired_rules = True
                self.working_memory = self.working_memory.union(rule.fire(self.working_memory))
                self.fired_rules.add((rule.id, rule.description))
            if not has_fired_rules:
                break

    
    def backward_chaining(self, goal):
        self.reset_working_memory()
        goals = set(goal)
        while len(goals) >= 1:
            for rule in self.rules:
                if rule.consequences == goals[-1]:
                    if len(rule.fire(self.working_memory)) == 0:
                        goals = goals.union(rule.antecedents)
                    else:
                        self.working_memory = self.working_memory.union(rule.fire(self.working_memory))
                        goals = goals.difference(rule.consequences)
                        self.fired_rules.add((rule.id, rule.description))
                
    
class LoveTheoryRule:
    rule_count = 0

    def __init__(self, a, c, d, p = lambda x, y: x.issubset(y)):
        LoveTheoryRule.rule_count += 1
        self.id = LoveTheoryRule.rule_count
        self.antecedents = a
        self.consequences = c
        self.description = d
        self.predicate = p
    
    def fire(self, memory):
        if self.predicate(self.antecedents, memory):
            return self.consequences
        return ""
    

agent = LoveTheoryAgent()
rules = {
    LoveTheoryRule(agent.intimacy_points, {"intimacy"}, "If intimacy_points > (total_points / 2), then intimacy.", lambda x, y: x > 3),
    LoveTheoryRule(agent.passion_points, {"passion"}, "If passion_points > (total_points / 2), then passion.", lambda x, y: x > 3,),
    LoveTheoryRule(agent.commitment_points, {"commitment"}, "If commitment_points > (total_points / 2), then commitment.", lambda x, y: x > 3),

    LoveTheoryRule(set(), {"nonlove"}, "If intimacy, passion, commitment are all absent, then nonlove."),
    LoveTheoryRule({"intimacy"}, {"friendship"}, "If intimacy, then friendship."),
    LoveTheoryRule({"passion"}, {"infatuation"}, "If passion, then infatuation."),
    LoveTheoryRule({"commitment"}, {"empty love"}, "If commitment, then empty love."),
    LoveTheoryRule({"intimacy", "passion"}, {"romantic love"}, "If intimacy and passion, then romantic love."),
    LoveTheoryRule({"intimacy", "commitment"}, {"companionate love"}, "If intimacy and commitment, then companionate love."),
    LoveTheoryRule({"commitment", "passion"}, {"fatuous love"}, "If commitment and passion, then fatuous love."),
    LoveTheoryRule({"intimacy", "commitment", "passion"}, {"consummate love"}, "If intimacy, commitment and passion, then consummate love."),

    LoveTheoryRule({"nonlove"}, {"nonlove description"}, "If nonlove, then nonlove description."),
    LoveTheoryRule({"friendship"}, {"friendship description"}, "If friendship, then friendship description."),
    LoveTheoryRule({"infatuation"}, {"infatuation description"}, "If infatuation, then infatuation description."),
    LoveTheoryRule({"empty love"}, {"empty love description"}, "If empty love, then empty love description."),
    LoveTheoryRule({"romantic love"}, {"romantic love description"}, "If romantic love, then romantic love description."),
    LoveTheoryRule({"companionate love"}, {"companionate love description"}, "If companionate love, then companionate love description."),
    LoveTheoryRule({"fatuous love"}, {"fatuous love description"}, "If fatuous love, then fatuous love description."),
    LoveTheoryRule({"consummate love"}, {"consummate love description"}, "If consummate love, then consummate love description.")
}

agent.set_rules(rules)


        
                




