# Imports
import random

# Local imports
from evennia import Command
from evennia import CmdSet
from evennia import default_cmds
from evennia import create_script
from commands import command
from world.combat_loop import CombatLoop


class Helper():
    """
    Class for general combat helper commands.
    """

    def __init__(self, caller):
        self.caller = caller


    def targetHandler(self, target):
        # Check for designated target
        target = self.caller.search(target)

        if not target:
            self.caller.msg("|540Target not found.|n")
            return

        if target == self.caller:
            self.caller.msg(f"|400{self.caller}, you had better not try that.|n")
            return

        if target.db.body is None:
            self.caller.msg("|400You had better not try that.|n")
            return

        return target


    def canFight(self, caller):
        can_fight = True if caller.db.bleed_points else False

        return can_fight


    def isAlive(self, target):
        is_alive = True if target.db.death_points else False

        return is_alive


    def weaponValue(self, level):
        """
        Returns bonus for weapon level based on value set
        """
        if level == 1:
            bonus = 2
        elif level == 2:
            bonus = 4
        elif level == 3:
            bonus = 6
        elif level == 4:
            bonus = 8
        else:
            bonus = 0

        return bonus


    def masterOfArms(self, level):
        """
        Returns die result based on master of arms level
        """
        if level == 0:
            die_result = random.randint(1,6)
        elif level == 1:
            die_result = random.randint(1,10)
        elif level == 2:
            die_result = random.randint(1,6) + random.randint(1,6)
        elif level == 3:
            die_result = random.randint(1,8) + random.randint(1,8)

        return die_result

    def wyldingHand(self, level):
        """
        Returns die result based on wylding hand level
        """
        if level == 0:
            die_result = random.randint(1,6)
        elif level == 1:
            die_result = random.randint(1,10)
        elif level == 2:
            die_result = random.randint(1,6) + random.randint(1,6)
        elif level == 3:
            die_result = random.randint(1,8) + random.randint(1,8)

        return die_result

    def shotFinder(self, targetArray):
        """
        Rolls a number between 1 and 5 and then maps it to an area of the body for the hit
        """
        # Roll a d5 and then map the result to the targetArray.
        # Return the value from the target array and remove it from the current character's targetArray value in the db

        # Roll random number
        result = random.randint(0,5)

        # Get part of body based on targetArray input
        target = targetArray[result]

        return target


    def bodyChecker(self, bodyScore):
        """
        Just checks amount of body and applies penalty based on number character is down.
        """
        if bodyScore >= 3:
            damage_penalty = 0
        elif bodyScore == 2:
            damage_penalty = 1
        elif bodyScore == 1:
            damage_penalty = 2
        elif bodyScore == 0:
            damage_penalty = 3
        elif bodyScore == -1:
            damage_penalty = 4
        elif bodyScore == -2:
            damage_penalty = 5
        else:
            damage_penalty = 6

        return damage_penalty

    def weaknessChecker(self, hasWeakness):
        """
        Checks to see if caller has weakness and then applies corresponding penalty.
        """
        attack_penalty = 2 if hasWeakness else 0

        return attack_penalty

    def deathSubtractor(self, damage, target, caller):
        """
        Handles damage at or below 3 body.
        """
        target_body = target.db.body
        target_bleed_points = target.db.bleed_points
        target_death_points = target.db.death_points

        if target_body and damage:
            body_damage = target_body - damage
            if body_damage < 0:
                damage = abs(body_damage)
                target.db.body = 0
            else:
                target.db.body = body_damage
                damage = 0

            target.location.msg_contents(f"{caller.key} greviously wounds {target.key}.")


        if target_bleed_points and damage:
            bleed_damage = target_bleed_points - damage
            if bleed_damage < 0:
                damage = abs(bleed_damage)
                target.db.bleed_points = 0
            else:
                target.db.bleed_points = bleed_damage
                damage = 0

            target.msg("|540You are bleeding profusely from many wounds and can no longer use any active martial skills.\nYou may only use the limbs that have not been injured.|n")
            target.location.msg_contents(f"|015{target.key} is bleeding profusely from many wounds and will soon lose consciousness.|n")


        if target_death_points and damage:
            death_damage = target_death_points - damage
            if death_damage < 0:
                damage = abs(death_damage)
                target.db.death_points = 0
            else:
                target.db.death_points = death_damage
                damage = 0

            target.msg("|400You are unconscious and can no longer move of your own volition.|n")
            target.location.msg_contents(f"|015{target.key} does not seem to be moving.|n")

        else:
            pass


    def damageSubtractor(self, damage, target, caller):
        """
        Takes attack type of caller and assigns damage based on target stats.
        """
        # Build the target av objects
        target_shield_value = target.db.shield_value  # Applied conditionally
        target_armor = target.db.armor
        target_tough = target.db.tough
        target_body = target.db.body
        target_armor_specialist = target.db.armor_specialist
        target_armor_value = target.db.av
        target_bleed_points = target.db.bleed_points
        target_death_points = target.db.death_points

        # Apply damage in order
        if target_shield_value:
            # Get value of shield damage to check if it's under 0. Need to pass
            # this on to armor
            shield_damage = target_shield_value - damage
            if shield_damage < 0:
                # Check if damage would make shield go below 0
                damage = abs(shield_damage)
                # Set shield_value to 0
                target.db.shield_value = 0
                # Recalc and set av with new shield value
            else:
                target.db.shield_value = shield_damage
                damage = 0

        if target_armor_specialist and damage:
            # Get value of damage
            armor_specialist_damage = target_armor_specialist - damage
            if armor_specialist_damage < 0:
                damage = abs(armor_specialist_damage)
                target.db.armor_specialist = 0
            else:
                target.db.armor_specialist = armor_specialist_damage
                damage = 0

        if target_armor and damage:
            # Get value of damage
            armor_damage = target_armor - damage
            if armor_damage < 0:
                damage = abs(armor_damage)
                target.db.armor = 0
            else:
                target.db.armor = armor_damage
                test = target_shield_value + target.db.armor + target_tough + target_armor_specialist
                damage = 0

        if target_tough and damage:
            tough_damage = target_tough - damage
            if tough_damage < 0:
                damage = abs(tough_damage)
                target.db.tough = 0
            else:
                target.db.tough = tough_damage
                damage = 0
        else:
            self.deathSubtractor(damage, target, caller)

        new_av = self.updateArmorValue(target.db.shield_value, target.db.armor, target.db.tough, target.db.armor_specialist)

        return new_av


    def updateArmorValue(self, shieldValue, armor, tough, armorSpecialist):
        armor_value = shieldValue + armor + tough + armorSpecialist

        return armor_value


    def getMeleeCombatStats(self, combatant):
        # Get hasMelee for character to check that they've armed themselves.
        melee = combatant.db.melee
        two_handed = combatant.db.twohanded
        bow = combatant.db.bow

        # Vars for melee attack_result logic
        master_of_arms = combatant.db.master_of_arms
        weapon_level = self.weaponValue(combatant.db.weapon_level)
        wylding_hand = combatant.db.wylding_hand

        # Penalties
        weakness = self.weaknessChecker(combatant.db.weakness)
        dmg_penalty = self.bodyChecker(combatant.db.body)

        # Slot checks for sunder command
        left_slot = combatant.db.left_slot
        right_slot = combatant.db.right_slot

        melee_stats = {"melee": melee,
                       "bow": bow,
                       "bow_penalty": 2,
                       "two_handed": two_handed,
                       "master_of_arms": master_of_arms,
                       "weapon_level": weapon_level,
                       "wylding_hand": wylding_hand,
                       "weakness": weakness,
                       "dmg_penalty": dmg_penalty,
                       "left_slot": left_slot,
                       "right_slot": right_slot,
                       "disarm_penalty": 2,
                       "stagger_penalty": 2,
                       "stagger_damage": 2}

        return melee_stats


    def fayneChecker(self, master_of_arms, wylding_hand):
        # Return die roll based on level in master of arms or wylding hand.
        if wylding_hand:
            die_result = self.wyldingHand(wylding_hand)
        else:
            die_result = self.masterOfArms(master_of_arms)

        return die_result



"""
Active Martial Skills
"""



class CmdResist(Command):
    """
    Issues a resist command.

    Usage:

    resist

    This will issue a resist command that adds one to your body, and decrements one from a character's available resists.
    """

    key = "resist"
    help_category = "mush"

    def func(self):
        h = Helper()

        "Get level of master of arms for base die roll. Levels of gear give a flat bonus of +1/+2/+3."
        resistsRemaining = self.caller.db.resist
        master_of_arms = self.caller.db.master_of_arms
        wylding_hand = self.caller.db.wyldinghand
        weapon_level = h.weaponValue(self.caller.db.weapon_level)


        # Check for weakness on character
        weakness = h.weaknessChecker(self.caller.db.weakness)

        # Check for equip proper weapon type or weakness
        if weakness:
            self.caller.msg("|400You are too weak to use this attack.|n")
        elif resistsRemaining > 0:
        # Return die roll based on level in master of arms or wylding hand.
            if wylding_hand:
                die_result = h.wyldingHand(wylding_hand)
            else:
                die_result = h.masterOfArms(master_of_arms)

            # Decrement amount of cleaves from amount in database
            self.caller.db.resist -= 1

            # Get final attack result and damage
            weakness = h.weaknessChecker(self.caller.db.weakness)
            dmg_penalty = h.bodyChecker(self.caller.db.body)
            attack_result = (die_result + weapon_level) - dmg_penalty - weakness

            self.caller.location.msg_contents(f"|015{self.caller.key} resists the attack, taking no damage!.|n")
            self.caller.db.body += 1
            self.caller.msg(f"|540Resist adds one body back to your total.\nYour new total body value is {self.caller.db.body}|n")
        else:
            self.caller.msg("|400You have 0 resists remaining or do not have the skill.")


class CmdStun(Command):
    """
    Issues a stun command.

    Usage:

    stun <target>

    This will issue a stun command that denotes a target of an attack will lose their next turn if they are hit.
    """

    key = "stun"
    help_category = "mush"

    def parse(self):
        "Very trivial parser"
        self.target = self.args.strip()


    def func(self):
            h = Helper()

            "Get level of master of arms for base die roll. Levels of gear give a flat bonus of +1/+2/+3."
            stunsRemaining = self.caller.db.stun
            master_of_arms = self.caller.db.master_of_arms
            hasBow = self.caller.db.bow
            hasMelee = self.caller.db.melee
            weapon_level = h.weaponValue(self.caller.db.weapon_level)
            hasTwoHanded = self.caller.db.twohanded

            wylding_hand = self.caller.db.wyldinghand

            if not self.args:
                self.caller.msg("|540Usage: stun <target>|n")
                return

            target = self.caller.search(self.target)

            if not target:
                self.caller.msg("|400There is nothing here that matches that description.|n")
                return

            if target == self.caller:
                self.caller.msg(f"|400Don't stun yourself {self.caller}!|n")
                return

            if target.db.body is None:
                self.caller.msg("|400You had better not try that.")
                return

            # Check for weakness on character
            weakness = h.weaknessChecker(self.caller.db.weakness)

            # Check for equip proper weapon type or weakness
            if weakness:
                self.caller.msg("|400You are too weak to use this attack.|n")
            elif hasBow:
                self.caller.msg("|540Before you can attack, you must first unequip your bow using the command setbow 0.")
            elif not hasMelee or not hasTwoHanded:
                self.caller.msg("|540Before you can attack, you must first equip a melee weapon using the command setmelee 1 or settwohanded 1.")
            else:
                if stunsRemaining > 0:
                # Return die roll based on level in master of arms or wylding hand.
                    if wylding_hand:
                        die_result = h.wyldingHand(wylding_hand)
                    else:
                        die_result = h.masterOfArms(master_of_arms)

                    # Decrement amount of disarms from amount in database
                    self.caller.db.stun -= 1

                    # Get final attack result and damage
                    weakness = h.weaknessChecker(self.caller.db.weakness)
                    dmg_penalty = h.bodyChecker(self.caller.db.body)
                    attack_result = (die_result + weapon_level) - dmg_penalty - weakness

                    # Return attack result message

                    if attack_result > target.db.av:
                        self.caller.location.msg_contents(f"|015{self.caller.key}|n (|020{attack_result}|n) |015stuns {target.key}|n (|400{target.db.av}|n) |015such that they're unable to attack for a moment.|n\n|540{target.key} may noy attack next round.|n")
                    elif attack_result < target.db.av:
                        self.caller.location.msg_contents(f"|015{self.caller.key} attempts|n (|400{attack_result}|n)|015 to stun {target.key}|n (|020{target.db.av}|n)|015, but fumbles their attack.|n")
                else:
                    self.caller.msg("|400You have 0 stuns remaining or do not have the skill.|n")


class CmdStagger(Command):
    """
    Issues a stagger command.

    Usage:

    stagger <target>

    This will calculate an attack score based on your weapon and master of arms level.
    """

    key = "stagger"
    help_category = "mush"

    def parse(self):
        "Very trivial parser"
        self.target = self.args.strip()

        if not self.target:
            self.caller.msg("|540Usage: stagger <target>|n")
            return

    def func(self):
        h = Helper()

        "Get level of master of arms for base die roll. Levels of gear give a flat bonus of +1/+2/+3."
        master_of_arms = self.caller.db.master_of_arms
        hasBow = self.caller.db.bow
        hasMelee = self.caller.db.melee
        staggersRemaining = self.caller.db.stagger
        weapon_level = h.weaponValue(self.caller.db.weapon_level)
        hasTwoHanded = self.caller.db.twohanded
        stagger_penalty = 2

        wylding_hand = self.caller.db.wyldinghand

        target = self.caller.search(self.target)

        if not target:
            self.caller.msg("|400There is nothing here that matches that description.|n")
            return

        if target == self.caller:
            self.caller.msg(f"|400Don't stagger yourself {self.caller}, silly!|n")
            return

        if target.db.body is None:
            self.caller.msg("|400You had better not try that.")
            return

        # Check for equip proper weapon type
        # Check for weakness on character
        weakness = h.weaknessChecker(self.caller.db.weakness)

        # Check for equip proper weapon type or weakness
        if weakness:
            self.caller.msg("|400You are too weak to use this attack.|n")
        elif hasBow:
            self.caller.msg("|540Before you can attack, you must first unequip your bow using the command setbow 0.")
        elif not hasMelee or not hasTwoHanded:
            self.caller.msg("|540Before you can attack, you must first equip a weapon using the command setmelee 1 or settwohanded 1.")
        else:
            if staggersRemaining > 0:
            # Return die roll based on level in master of arms or wylding hand.
                if wylding_hand:
                    die_result = h.wyldingHand(wylding_hand)
                else:
                    die_result = h.masterOfArms(master_of_arms)

                # Decrement amount of cleaves from amount in database
                self.caller.db.stagger -= 1

                # Get final attack result and damage
                weakness = h.weaknessChecker(self.caller.db.weakness)
                dmg_penalty = h.bodyChecker(self.caller.db.body)
                attack_result = (die_result + weapon_level) - dmg_penalty - weakness - stagger_penalty

                # Return attack result message
                if attack_result > target.db.av:
                    self.caller.location.msg_contents(f"|015{self.caller.key}|n (|020{attack_result}|n) |015staggers {target.key}|n (|400{target.db.av}|n) |015, putting them off their guard.|n")
                    # subtract damage from corresponding target stage (shield_value, armor, tough, body)
                    new_av = h.damageSubtractor(2, target)
                    # Update target av to new av score per damageSubtractor
                    target.db.av = new_av
                    target.msg(f"|540Your new total Armor Value is {new_av}:\nShield: {target.db.shield}\nArmor Specialist: {target.db.armor_specialist}\nArmor: {target.db.armor}\nTough: {target.db.tough}|n")

                elif attack_result < target.db.av:
                    self.caller.location.msg_contents(f"|015{self.caller.key} attempts|n (|400{attack_result}|n)|015 to stagger {target.key}|n (|020{target.db.av}|n)|015, but fumbles their attack.|n")
            else:
                self.caller.msg("|400You have 0 staggers remaining or do not have the skill.|n")




"""
Knight commands
"""

class CmdBattlefieldCommander(Command):
    """
    Usage: bolster <speech>

    Use the bolster command followed by a speech to give all in the room 1 tough.
    """
    key = "bolster"
    aliases = ["battlefieldcommander"]
    help_category = "combat"

    def parse(self):
        "Very trivial parser"
        self.speech = self.args.strip()

    def func(self):
        if not self.args:
            self.caller.msg("|540Usage: bolster <target>|n")
            return

        bolsterRemaining = self.caller.db.battlefieldcommander

        if bolsterRemaining > 0:
            self.caller.location.msg_contents(f"|015Amidst the chaos of the fighting, {self.caller.key} shouts so all can hear,|n |400{self.speech}|n.\n|540Everyone in the room may now add 1 Tough to their av, using the command settough #|n |400(Should be one more than your current value).|n")
            self.caller.db.battlefieldcommander -= 1
        else:
            self.caller.msg("|400You have no uses of your battlefield commander ability remaining or do not have the skill.|n")


class CmdRally(Command):
    """
    Usage: rally <speech>

    Use the rally command followed by a speech to remove a fear effect from those in the room.
    """
    key = "rally"
    help_category = "combat"

    def parse(self):
        "Very trivial parser"
        self.speech = self.args.strip()

    def func(self):
        if not self.args:
            self.caller.msg("|540Usage: rally <speech>|n")
            return

        rallyRemaining = self.caller.db.rally

        if rallyRemaining > 0:
            self.caller.location.msg_contents(f"|015{self.caller.key} shouts so all can hear,|n |400{self.speech}|n.\n|540Everyone in the room now feels unafraid. Cancel the fear effect.|n")
            self.caller.db.rally -= 1
        else:
            self.caller.msg("|400You have no uses of your rally ability remaining or do not have the skill.|n")
