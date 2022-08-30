# py_rete

[![Build Status](https://app.travis-ci.com/cmaclell/py_rete.svg?branch=master)](https://app.travis-ci.com/cmaclell/py_rete) [![Coverage Status](https://coveralls.io/repos/github/cmaclell/py_rete/badge.svg?branch=master)](https://coveralls.io/github/cmaclell/py_rete?branch=master)

## Introduction

The py_rete project aims to implement a Rete engine in native python. This
system is built using one the description of the Rete algorithms provided by
[Doorenbos (1995)][doorenbos]. It also makes heavy use of ideas from the
[Experta project][experta] (although no code is used from this project as it
utilizes an LGPL license).

The purpose of this system is to support basic expert / production system AI
capabilities in a way that is easy to integrate with other Python based AI/ML
systems.

## Installation

This package is installable via pip with the following command:
`pip install -U py_rete`.

It can also be installed directly from GitHub with the following command:
`pip install -U git+https://github.com/cmaclell/py_rete@master`

## The Basics

The two high-level structures to support reasoning with py_rete are **facts**
and **productions**. 

### Facts

Facts represent the basic units of knowledge that the productions match over.
Here are a few examples of facts and how they work.

1. *Facts* are a subclass of dict, so you can treat them similar to dictionaries.

```python
>>> f = Fact(a=1, b=2)
>>> f['a']
1
```

2. *Facts* extend dictionaries, so they also support positional values without
   keys. These values are assigned numerical indices based on their position.

```python
>>> f = Fact('a', 'b', 'c')
>>> f[0]
'a'
```

3. *Facts* can support mixed positional and named arguments, but positional
   must come before named and named arguments do not get positional references.

```python
>>> f = Fact('a', 'b', c=3, d=4)
>>> f[0]
'a'
>>> f['c']
3
```

5. *Facts* support nesting with other facts. 

```python
>>> f = Fact(subfact=Fact())
Fact(subfact=Fact())
```

Note that there will be issues if facts contain other data structures that
contain facts (they will not be properly added to the rete network or to
productions).

### Productions

Similar to Experta's rules, *Productions* are functions that are decorated with
conditions that govern when they execute and bind the arguments necessary for
their execution.

*Productions* have two components:
* Conditions, which are essentially facts that can contain pattern matching
  variables.
* A Function, which is executed for each rule match, with the arguments to the
  function being passed the bindings from pattern matching variables.

Here is an example of a simple *Productions* that binds with all *Facts* that
have the color red and prints 'I found something red' for each one:

```python
@Production(Fact(color='red'))
def alert_something_red():
    print("I found something red")
```

Productions also support logical operators to express more complex conditions.

```python
@Production(AND(OR(Fact(color='red'),
                   Fact(color='blue')),
	        NOT(Fact(color='green'))))
def alert_something_complex():
    print("I found something red or blue without any green present")
```

Bitwise logical operators can be used as shorthand to make composing complex conditions easier.
```python
@Production((Fact(color='red') | Fact(color='blue')) & ~Fact(color='green'))
def alert_something_complex2():
    print("I found something red or blue without any green present")
```

In addition to matching simple facts, pattern matching variables can be used to
match values from Facts. Matching ensures that variable bindings are consistent
across conditions. Additionally, variables are passed to arguments in the function
with the same name during matching. For example, the following production finds
a Fact with a lastname attribute.  For each Fact it finds, it prints "I found a
fact with a lastname attribute: `<lastname>`".  Note, the `V('lastname')`
corresponds to a variable named lastname that can bind with values from Facts
during matching.  Additionally the variable (`V('lastname')`) and the function
argument `lastname` match have the same name, which enables the matcher to the
variable bindings into the function.
```python
@Production(Fact(lastname=V('lastname')))
def found_relatives(lastname):
    print("I found a fact with a lastname: {}".format(lastname))
```

It is also possible to employ functional tests (lambdas or functions) using
`Filter` conditions. Like the function that is being decorated, Filter
conditions pass variable bindings to their equivelently named function
arguments. It is important to note that positive facts that bind with these
variables need to be listed in the production before the tests that use them.
```python
@Production(Fact(value=V('a')) &
            Fact(value=V('b')) &
            Filter(lambda a, b: a > b) &
            Fact(value=V('c')) &
            Filter(lambda b, c: b > c))
def three_values(a, b, c):
    print("{} is greater than {} is greater than {}".format(a, b, c))
```

It is also possible to bind *facts* to variables as well, using the bitshift
operator.
```python
@Production(V('name_fact') << Fact(name=V('name')))
def found_name(name_fact):
    print("I found a name fact {}".format(name_fact))
```

### ReteNetwork

To engage in reasoning *facts* and *productions* are loaded into a
**ReteNetwork**, which facilitates the matching and application of productions
to facts.

Here is how you create a network:

```python
net = ReteNetwork()
```

Once a network has been created, then facts can be added to it.
```python
f1 = Fact(light_color="red")
net.add_fact(f1)
```

Note, facts added to the network cannot contain any variables or they will
trigger an exception when added. Additionally, once a fact has been added to
network it is assigned a unique internal identifier.

This makes it possible to update the fact.
```python
f1['light_color'] = "green"
net.update_fact(f1)
```

It also make it possible to remove the fact.
```python
net.remove_fact(f1)
```

When updating a fact, note that it is not updated in the network until
the `update_fact` method is called on it. An update essentially equates to
removing and re-adding the fact.

Productions can also be added to the network. Productions also can make use of
the `net` variable, which is automatically bound to the Rete network the
production has been added to. This makes it possible for productions to update
the contents of the network when they are fired. For example, the following functions
have an argument called `net` that is bound to the rete network even though there is
no variable by that name in the production conditions.
```python
>>> f1 = Fact(light_color="red")
>>> 
>>> @Production(V('fact') << Fact(light_color="red"))
>>> def make_green(net, fact):
>>>	print('making green')
>>>     fact['light_color'] = 'green'
>>>     net.update_fact(fact)
>>> 
>>> @Production(V('fact') << Fact(light_color="green"))
>>> def make_red(net, fact):
>>>	print('making red')
>>>     fact['light_color'] = 'red'
>>>     net.update_fact(fact)
>>> 
>>> light_net = ReteNetwork()
>>> light_net.add_fact(f1)
>>> light_net.add_production(make_green)
>>> light_net.add_production(make_red)
```

Once the above fact and productions have been added the network can be run.
```python
>>> light_net.run(5)
making green
making red
making green
making red
making green
```

The number passed to run denotes how many rules the network should fire
before terminating.

In addition to this high-level function for running the network, there
are also some lower-level capabilities that can be used to more closely control
the rule execution.

For example, you can get all the production matches from the matches property.
```体彩例子说明
1、事实（fact）  --  对象之间及对象属性之间的多元关系。
物模型是对象属性之间关系，事实用一个三元组来表示：(identifier ^attribute value)

W1: 体彩票, 期号，21105
W2: 体彩票, 序列号，112233-121311-187632-192345
W3: 体彩票, 开奖时间，2021-12-13
W4: 体彩票, 前区号码: (‘09’, ‘18’, ‘19’, ‘29’, ‘30’)
W5: 体彩票, 后区号码: (‘04’, ‘11’)
W6: 开奖票，期号，21105
W7: 开奖票，开奖时间，2021-12-13
W8: 开奖票, 前区号码: (‘09’, ‘17’, ‘19’, ‘29’, ‘34’)
W9: 开奖票, 后区号码: (‘04’, ‘11’)

2、规则（rule）  --  由条件和结论构成的推理语句，当存在事实满足条件时，相应结论被激活。

一等奖：投注号码与当期开奖号码全部相同(顺序不限，下同)，即中奖；
 
二等奖：投注号码与当期开奖号码中的五个前区号码及任意一个后区号码相同，即中奖；
 
三等奖：投注号码与当期开奖号码中的五个前区号码相同，即中奖；
 
四等奖：投注号码与当期开奖号码中的任意四个前区号码及两个后区号码相同，即中奖；
 
五等奖：投注号码与当期开奖号码中的任意四个前区号码及任意一个后区号码相同，即中奖；
 
六等奖：投注号码与当期开奖号码中的任意三个前区号码及两个后区号码相同，即中奖；
 
七等奖：投注号码与当期开奖号码中的任意四个前区号码相同，即中奖；
 
八等奖：投注号码与当期开奖号码中的任意三个前区号码及任意一个后区号码相同，或者任意两个前区号码及两个后区号码相同，即中奖；
 
九等奖：投注号码与当期开奖号码中的任意三个前区号码相同，或者任意一个前区号码及两个后区号码相同，或者任意两个前区号码及任意一个后区号码相同，或者两个后区号码相同，即中奖。

3、建立数据模型

<SPORTS_LOTTERY_ID>	^sl_issue_no		<issue_serial_number>	# 21105
<SPORTS_LOTTERY_ID>	^sl_time			<lottery_valid_date>		# 20210911
<SPORTS_LOTTERY_ID>	^sl_front_area		<ticket_fa_list>			# [11, 25, 26, 27, 33]
<SPORTS_LOTTERY_ID>	^sl_back_area		<ticket_ba_list>			# [01, 06]

run_lottery				^rl_issue_no		<issue_serial_number>	# 21105
run_lottery				^rl_time		<lottery_valid_date>	# 20210911
run_lottery				^rl_front_area		<rl_fa_list>		# [11, 25, 26, 27, 33]
run_lottery				^rl_back_area		<rl_ba_list>		# [01, 06]

4、建立产品
C1 = Cond(V('SPORTS_LOTTERY_ID'), 'sl_issue_no', V('issue_serial_number'))
C2 = Cond(V('SPORTS_LOTTERY_ID'), 'sl_time', V('lottery_valid_date'))
C3 = Cond(V('SPORTS_LOTTERY_ID'), 'sl_front_area', V('ticket_fa_list'))
C4 = Cond(V('SPORTS_LOTTERY_ID'), 'sl_back_area', V('ticket_ba_list'))

C5 = Cond('run_lottery', 'rl_issue_no', V('issue_serial_number'))
C6 = Cond('run_lottery', 'rl_time', V('lottery_valid_date'))
C7 = Cond('run_lottery', 'rl_front_area', V('rl_fa_list'))
C8 = Cond('run_lottery', 'rl_back_area', V('rl_ba_list'))

front_area_bind = Bind(lambda ticket_fa_list, rl_fa_list: len(set(ticket_fa_list) & set(rl_fa_list)), V('fa_guessed'))
fa_f0 = Filter(lambda fa_guessed: fa_guessed == 0)
fa_f1 = Filter(lambda fa_guessed: fa_guessed == 1)
fa_f2 = Filter(lambda fa_guessed: fa_guessed == 2)
fa_f3 = Filter(lambda fa_guessed: fa_guessed == 3)
fa_f4 = Filter(lambda fa_guessed: fa_guessed == 4)
fa_f5 = Filter(lambda fa_guessed: fa_guessed == 5)

back_area_bind = Bind(lambda ticket_ba_list, rl_ba_list: len(set(ticket_ba_list) & set(rl_ba_list)), V('ba_guessed'))
ba_f0 = Filter(lambda ba_guessed: ba_guessed == 0)
ba_f1 = Filter(lambda ba_guessed: ba_guessed == 1)
ba_f2 = Filter(lambda ba_guessed: ba_guessed == 2)

```

[experta]: https://github.com/nilp0inter/experta
[doorenbos]: http://reports-archive.adm.cs.cmu.edu/anon/1995/CMU-CS-95-113.pdf
