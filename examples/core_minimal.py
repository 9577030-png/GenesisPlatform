from genesis_core import Condition, Fact, Rule, RuleEngine


rule = Rule(
    id="high_value",
    conditions=(Condition("amount", ">", 1000),),
    result={"action": "review"},
)

result = RuleEngine().evaluate(
    (rule,),
    (Fact("amount", 1500),),
)

print(result[0])
