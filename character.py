from abc import ABC, abstractmethod
from random import choice

BASE_LEVEL_EXP = 200

class Character:
    def __init__(self, name: str, maxHp: int, Pow: int, Def: int, Spd: int) -> None:
        self.name = name
        self.Hp = maxHp
        self.Pow = Pow
        self.PowBuff = 0
        self.PowNerf = 0
        self.Def = Def
        self.DefBuff = 0
        self.DefNerf = 0
        self.Spd = Spd
        self.maxHp = maxHp
        self.status = CharacterStatus()
        # {
        #     'burn'      : False, # Continuously take damage during the duration (if the damage is fire damage)
        #     'burn-dur'  : 0,
        #     'guard'     : False, # Skip turn, and immediately attack after being attacked
        #     'poisoned'  : False, # Continuously take damage until cured or Hp = 1
        #     'healing'   : False, # Continuously heal during the duration
        #     'heal-dur'  : 0,
        #     'sleep'     : False, # When true, the character will skip turn until attacked or end of duration
        #     'sleep-dur' : 0,
        #     'knocked'   : False, # True if Hp <= 0, Unable to play until revived
        #     'pow-buff-dur'  : 0,
        #     'pow-nerf-dur'  : 0,
        #     'def-buff-dur'  : 0,
        #     'def-nerf-dur'  : 0,
        # }
        self.skills = []
    
    def add_skill(self, skill: 'Skill'):
        self.skills.append(skill)
    
    def take_damage(self, dmg: int):
        self.Hp -= round(dmg - 0.01 * (self.Def + self.DefBuff - self.DefNerf) - dmg * 0.2 * (self.status.guard or self.status.counter))
        if self.Hp < 0:
            self.Hp = 0
            self.status.knocked_out()
    
    def restore_Hp(self, amount: int):
        self.Hp = min(self.Hp + amount, self.maxHp)

class PlayableCharacter(Character):
    def __init__(self, name: str, maxHp: int, maxSp: int, Pow: int, Def: int, Spd: int) -> None:
        super().__init__(name, maxHp, Pow, Def, Spd)
        self.Sp = maxSp
        self.maxSp = maxSp
        self.level = 1
        self.Exp = 0
        self.nextLevelExp = BASE_LEVEL_EXP
        self.items = []
    
    def recover_Sp(self, amount: int):
        self.Sp = min(self.Sp + amount, self.maxSp)
    
    def pay_skill(self, amount: int):
        ''' Pay for the skill with Sp'''
        self.Sp -= amount

class EnemyCharacter(Character):
    def __init__(self, name: str, maxHp: int, Pow: int, Def: int, Spd: int, strategy: function) -> None:
        super().__init__(name, maxHp, Pow, Def, Spd)
        self.strategy = strategy # Strategy(performer, target = {'ally' ..., 'opponent' ...})

class CharacterStatus:
    def __init__(self) -> None:
        self.burn = False       # Continuously take damage during the duration (if the damage is fire damage)
        self.guard = False      # Skip turn, parry incoming attack
        self.counter = False    # Skip turn, parry incoming attack followed by counter-attack
        self.poisoned = False   # Continuously take damage until cured or Hp = 1
        self.healing = False    # Continuously heal during the duration
        self.sleeping = False   # When true, the character will skip turn until attacked or end of duration
        self.frozen = False     # When true, the character will skip turn until end of duration
        self.knocked = False    # True if Hp <= 0, Unable to play until knocked = False
        self.burn_dura = 0
        self.poison_dura = 0
        self.heal_dura = 0
        self.sleep_dura = 0
        self.freeze_dura = 0
        self.pow_buff_dura = 0
        self.pow_nerf_dura = 0
        self.def_buff_dura = 0
        self.def_nerf_dura = 0
    
    def enable_burn(self, duration: int):
        self.burn, self.burn_dura = True, duration
    
    def disable_burn(self):
        self.burn, self.burn_dura = False, 0
    
    def enable_poison(self, duration: int):
        self.poisoned, self.poison_dura = True, duration
    
    def disable_poison(self):
        self.poisoned, self.poison_dura = False, 0

    def enable_healing(self, duration: int):
        self.healing, self.heal_dura = True, duration
    
    def disable_healing(self):
        self.healing, self.heal_dura = False, 0

    def enable_sleep(self, duration: int):
        self.sleeping, self.sleep_dura = True, duration
    
    def disable_sleep(self):
        self.sleeping, self.sleep_dura = False, 0
    
    def enable_freeze(self, duration: int):
        self.frozen, self.freeze_dura = True, duration

    def disable_freeze(self):
        self.frozen, self.freeze_dura = False, 0

    def enable_guard(self):
        self.guard = True
    
    def disable_guard(self):
        self.guard = False
    
    def enable_counter(self):
        self.counter = True
    
    def disable_counter(self):
        self.counter = False
    
    def knocked_out(self):
        self.knocked = True
    
    def revived(self):
        self.knocked = False

class PlayerAction:
    def __init__(self, performer: PlayableCharacter, target: EnemyCharacter|PlayableCharacter) -> None:
        self.performer = performer
        self.target = target
    
    def basic_attack(self):
        dmg = self.performer.Pow * 0.75
        self.target.take_damage(dmg)
        self.performer.recover_Sp(choice([2,3]))
    
    def use_skill(self, index):
        self.performer.skills[index].execute(self.performer, self.target)

    # def damage_skill(self, index):
    #     self.performer.skills[index](self.performer, self.target)
        # self.target.takeDamage(dmg)
        # self.performer.paySkill(price)
    
    # def heal_skill(self, index):
    #     self.performer.skills[index](self.performer, self.target)
        # self.target.restoreHp(healPower)
        # self.performer.paySkill(price)
    
    def do_nothing(self):
        # Just pass the turn
        pass

class EnemyAction:
    def __init__(self, performer: EnemyCharacter, target: EnemyCharacter|PlayableCharacter) -> None:
        self.performer = performer
        self.target = target

    def use_skill(self, index):
        self.performer.skills[index](self.performer, self.target)

    # def damage_skill(self, index):
    #     self.performer.skills[index](self.performer, self.target)
    #     self.target.takeDamage(dmg)
    
    # def heal_skill(self, index):
    #     self.performer.skills[index](self.performer, self.target)
    #     self.target.restoreHp(dmg)
    
    def do_nothing(self):
        # Just pass the turn
        pass

# Strategy
class Strategy(ABC):
    @abstractmethod
    def choose_action(self, performer: EnemyCharacter, target: list):
        pass

# Skills
class Skill(ABC):
    @abstractmethod
    def execute(self, performer: Character, target: Character) -> None:
        pass

# Damage
class Hit(Skill):
    def __init__(self) -> None:
        super().__init__()
        self.cost = 3

    def execute(self, performer: Character, target: Character) -> None:
        target.take_damage(performer.Pow)
        try:
            performer.pay_skill(self.cost) # exclusive to Players
        except AttributeError:
            return

class Ignition(Skill):
    def __init__(self) -> None:
        super().__init__()
        self.cost = 5
    
    def execute(self, performer: Character, target: Character) -> None:
        target.take_damage(round(performer.Pow * 1.5 + 0.2 * (performer.maxHp - performer.Hp)))
        target.status.enable_burn(1)
        try:
            performer.pay_skill(self.cost) # exclusive to Players
        except AttributeError:
            return

# def ignition(performer: Character, target: Character):
#     target.take_damage(round(performer.Pow * 1.5 + 0.2 * (performer.maxHp - performer.Hp)))
#     target.status.enable_burn(1)
#     try:
#         performer.paySkill(5) # exclusive to Players
#     except AttributeError:
#         return

# Heal/buff
class Heal(Skill):
    def __init__(self) -> None:
        super().__init__()
        self.cost = 4

    def execute(self, performer: Character, target: Character) -> None:
        target.restore_Hp(round(0.2 * target.maxHp + 0.1 * performer.Pow))
        try:
            performer.pay_skill(self.cost) # exclusive to Players
        except AttributeError:
            return

# Game Data
playableData = [PlayableCharacter('Patricia', 150, 24, 32, 24, 100),
]

enemyData = [EnemyCharacter('Crook', 120, 20, 20, 100, lambda: None),
             EnemyCharacter('Helmed Crook', 150, 20, 20, 100, lambda: None),
             EnemyCharacter('Puppet', 80, 30, 10, 120, lambda: None),
             EnemyCharacter('Devil Wasp', 150, 25, 35, 110, lambda: None)
]
