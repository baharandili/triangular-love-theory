import json
import random
from love_theory import LoveScale, LoveTheoryRule, LoveTheoryAgent

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
print(f"Please rate the following statements on a scale of {rating_min} to {rating_max} \
    ({rating_min} = Strongly Disagree, {rating_max} = Strongly Agree)")
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
    intimacy_points=love_points['intimacy'], passion_points=love_points['passion'], commitment_points=love_points['commitment'])

initialization = [
    LoveTheoryRule(agent.intimacy_points, {"intimacy"}, "If intimacy_points > (total_points / 2), then intimacy.",
                    lambda x, _: x >= (rating_max + rating_min) / 2 * len([l for l in love_scale if l.category == 'intimacy'])),
    LoveTheoryRule(agent.passion_points, {"passion"}, "If passion_points > (total_points / 2), then passion.",
                    lambda x, _: x >= (rating_max + rating_min) / 2 * len([l for l in love_scale if l.category == 'passion'])),
    LoveTheoryRule(agent.commitment_points, {"commitment"}, "If commitment_points > (total_points / 2), then commitment.",
                    lambda x, _: x >= (rating_max + rating_min) / 2 * len([l for l in love_scale if l.category == 'commitment']))
]

production = [
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
]

correction = [
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
]

agent.set_rules(initialization=initialization, production=production, correction=correction)

# Forward Chaining
if (method == 1):
    fired_rules = agent.forward_chaining()
    
# Backward Chaining
else:
    fired_rules, unsatisfied_antecedents = agent.backward_chaining("fatuous love")
    for u in unsatisfied_antecedents:
        print(u)    

for f in fired_rules:
    print(f)


