import json
import random
from love_theory import LoveScale, LoveTheoryRule, LoveTheoryAgent


def get_proper_input(value_range, *, input_prompt="", error_prompt="Invalid input."):
    user_in = input(input_prompt)
    while user_in not in value_range:
        print(error_prompt)
        user_in = input(input_prompt)
    return user_in


def get_formatted_string_from_iterables(iters):
    formatted_string = ""
    iters = list(iters)
    for i in iters:
        if not i == iters[-1]:
            formatted_string += f"{i}, "
        else:
            formatted_string += i
    return formatted_string


def get_love_types_key(s):
    if s == "empty love":
        return "emptyLove"
    if s == "romantic love":
        return "romanticLove"
    if s == "fatuous love":
        return "fatuousLove"
    if s == "companionate love":
        return "companionateLove"
    if s == "consummate love":
        return "consummateLove"
    return s


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

# TODO: Prompt the user about this program

# random.shuffle(love_scale)
print(f"Please rate the following statements on a scale of {rating_min} to {rating_max} \
    ({rating_min} = Strongly Disagree, {rating_max} = Strongly Agree)")

for l in love_scale:
    print(l.item)
    rating = int(get_proper_input([str(i) for i in range(rating_min, rating_max + 1)],
                                  error_prompt=f"Please enter a value betwen {rating_min} and {rating_max}."))
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
                   lambda x, y: x.issubset(y)),

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
    LoveTheoryRule({"nonlove", "intimacy"}, {"friendship"}, "If nonlove and intimacy, then friendship.",
                   lambda x, y: x == y),
    LoveTheoryRule({"nonlove", "passion"}, {"infatuation"}, "If nonlove and passion, then infatuation.",
                   lambda x, y: x == y),
    LoveTheoryRule({"nonlove", "commitment"}, {"empty love"}, "If nonlove and commitment, then empty love.",
                   lambda x, y: x == y),
    LoveTheoryRule({"nonlove", "intimacy", "passion"}, {"romantic love"}, "If nonlove, intimacy and passion, then romantic love.",
                   lambda x, y: x == y),
    LoveTheoryRule({"nonlove", "intimacy", "commitment"}, {"companionate love"}, "If nonlove, intimacy and commitment, then companionate love.",
                   lambda x, y: x == y),
    LoveTheoryRule({"nonlove", "passion", "commitment"}, {"fatuous love"}, "If nonlove, passion and commitment, then fatuous love.",
                   lambda x, y: x == y),
    LoveTheoryRule({"nonlove", "passion", "commitment", "intimacy"}, {"consummate love"}, "If nonlove, intimacy, passion and commitment, then consummate love.",
                   lambda x, y: x == y),

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

agent.set_rules(initialization=initialization,
                production=production, correction=correction)
print("Thanks for completing the questions! Here are two actions that I can perform: ")
print("1. Tell you which type of love exists between you and your companion. (Forward Chaining)")
print("2. You'll take a guess at the love type, and I'll verify if it is correct. (Backward Chaining)")
choice = int(get_proper_input(
    ["1", "2"], input_prompt="Please choose an option: "))

# Forward Chaining
if (choice == 1):
    fc_log = agent.forward_chaining()
    result = fc_log[-1][2]
    formatted_result = get_formatted_string_from_iterables(result)

    print(f"The love type that best describes your relationship currently is: {formatted_result}.")
    print(f"{love_types_dict[get_love_types_key(formatted_result)]}")
    print("")

    print("Fired production rules: ")
    if len(fc_log) == 0:
        print("None")
    else:
        for f in fc_log:
            print(f"{f[0]}. If {f[1]}, then {f[2]}.")

# Backward Chaining
else:
    print("Here are a list of love types: ")
    for index, rule in enumerate(agent.production_rules):
        print(f"{index}. {get_formatted_string_from_iterables(rule.consequences)}")
    index_num = [str(i) for i in range(len(agent.production_rules))]
    guessed_key = int(get_proper_input(index_num, input_prompt="Your guess is: ",
                                       error_prompt=f"Please enter a number between {index_num[0]} and {index_num[-1]}"))
    guess = agent.production_rules[guessed_key].consequences
    bc_log, unsatisfied_antecedents = agent.backward_chaining(guess)
    formatted_guess = get_formatted_string_from_iterables(guess)

    if len(unsatisfied_antecedents) > 0:
        print(f"Uhm... it looks like there is no {formatted_guess} between you and him/her... The important component(s) that are lacking in this relationship including: {get_formatted_string_from_iterables(unsatisfied_antecedents)}.")
        for a in unsatisfied_antecedents:
            print(f"{love_scale_dict[a]['definition']}")
        print("")

        fc_log = agent.forward_chaining()
        result = fc_log[-1][2]
        formatted_result = get_formatted_string_from_iterables(result)

        print(
            f"The love type that best describes your relationship currently is: {formatted_result}.")
        print(f"{love_types_dict[get_love_types_key(formatted_result)]}")
        print("")

    elif len(bc_log['corrected']) > 0:
        print(f"Your guess is wrong! But don't worry, your relationship is healthier than you think!")
        correction = bc_log['corrected'][-1][2]
        formatted_correction = get_formatted_string_from_iterables(correction)

        print(
            f"The love type that best describes your relationship currently is: {formatted_correction}.")
        print(f"{love_types_dict[get_love_types_key(formatted_correction)]}")
        print("")
        print("Fired correction rules: ")
        for c in bc_log['corrected']:
            print(f"{c[0]}. If {c[1]}, then {c[2]}.")
        print("")
    
    else: 
        print(f"Yes... you guessed it right. {formatted_guess} describes your relationship precisely.")
        print(f"{love_types_dict[get_love_types_key(formatted_guess)]}")
        print("")


    print("Fired production rules: ")
    if len(bc_log['fired']) == 0:
        print("None")
    else:
        for f in bc_log['fired']:
            print(f"{f[0]}. If {f[1]}, then {f[2]}.")
