import os, sys, re, random, string

#format for db
#{"_id":"kKv7GwOuFovGUWtK","name":"Blade Ward","type":"spell","img":"icons/svg/fire-shield.svg","data":{"description":{"value":"<p>You extend your hand and trace a sigil of warding in the air. Until the end of your next turn, you have resistance against bludgeoning, piercing, and slashing damage dealt by weapon attacks.</p>","chat":"","unidentified":""},"source":"Player's Handbook","activation":{"type":"action","cost":1,"condition":""},"duration":{"value":1,"units":"round"},"target":{"value":null,"width":null,"units":"self","type":""},"range":{"value":null,"long":null,"units":"self"},"uses":{"value":null,"max":"","per":""},"consume":{"type":"","target":"","amount":null},"ability":"","actionType":"other","attackBonus":"0","chatFlavor":"","critical":{"threshold":null,"damage":""},"damage":{"parts":[["","bludgeoning"]],"versatile":""},"formula":"","save":{"ability":"","dc":null,"scaling":"spell"},"level":0,"school":"abj","components":{"value":"","vocal":true,"somatic":true,"material":false,"ritual":false,"concentration":false},"materials":{"value":"","consumed":false,"cost":0,"supply":0},"preparation":{"mode":"prepared","prepared":false},"scaling":{"mode":"none","formula":""}},"effects":[{"_id":"RL134Mwf7zbeWje3","changes":[{"key":"Bludgeoning","mode":1,"value":"0.5"},{"key":"Piercing","mode":1,"value":"0.5"},{"key":"Slashing","mode":1,"value":"0.5"}],"disabled":false,"duration":{"rounds":1,"startTime":0},"icon":"icons/svg/shield.svg","label":"Resistance","origin":"Item.b4427ysQc5erIPuZ","transfer":true,"flags":{},"tint":"#cc0000"}],"folder":null,"sort":0,"permission":{"default":0,"EbhaPUSsc0xE98gi":3},"flags":{"core":{"sourceId":"Item.b4427ysQc5erIPuZ"}}}

#re patterns
src = re.compile("Source: (.+)")
lvl =

#spell db
spells = []

class Spell:
    def __init__(self, name, desc, source, casting_time, duration, target, action_type, level, school, components, concentration = False, ritual = False):
        self._id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        self.name = name
        self.img = "icons/magic/symbols/star-yellow.webp"
        self.description = desc
        self.source = source
        self.activation_type = casting_time[1]
        self.activation_cost = casting_time[0]
        self.duration_value = duration[0]
        self.duration_units = duration[1]
        self.target_value = target[0]
        self.target_type = target[1]
        self.target_units = target[2]
        self.range_value = range[0]
        self.range_units = range[1]
        self.actionType = action_type #rsak, msak, util, heal, save,,
        self.level = level
        self.school = school

        self.vocal = False
        self.somatic = False
        self.material = False
        self.mvalue = ""
        #components
        if "V" in components[0]:
            self.vocal = True
        if "S" in components[0]:
            self.somatic = True
        if "M" in components[0]:
            self.material = True
            self.mvalue = components[1]
        self.ritual = ritual
        self.concentration = concentration

        spells.append(self)

    def saveToDB(self):
        with open(os.path.join("packs", "spells.db"), "at", encoding="utf8") as db:
            db.write(f'{{"_id": {self._id},"name": {self.name},"type": "spell","img": {self.img},"data": {{"description": {{"value": {self.description},"chat": "","unidentified": ""}},"source": {self.src},"activation": {{"type": {self.activation_type},"cost": {self.activation_cost},"condition": ""}},"duration": {{"value": {self.duration_value},"units": {self.duration_units}}},"target": {{"value": {self.target_value},"width": null,"units": {self.target_units},"type": {self.target_type}}},"range": {{"value": {self.range_value},"long": null,"units": {self.range_units}}},"uses": {{"value": null,"max": "","per": ""}},"consume": {{"type": "","target": "","amount": null}},"ability": "","actionType": {self.actionType},"attackBonus": "0","chatFlavor": "","critical": {{"threshold": null,"damage": ""}},"damage": {{}},"formula": "","save": {{"ability": "","dc": null,"scaling": "spell"}},"level": {self.level},"school": {self.school},"components": {{"value": {self.mvalue},"vocal": {self.vocal},"somatic": {self.somatic},"material": {self.material},"ritual": {self.ritual},"concentration": {self.concentration}}},"materials": {{"value": {self.mvalue},"consumed": false,"cost": 0,"supply": 0}},"preparation": {{"mode": "prepared","prepared": false}},"scaling": {{"mode": "none","formula": ""}}}},"effects": [],"folder": null,"sort": 0,"permission": {{"default": 0}}}}')

def main():
    for html in os.listdir("src"):
        with open(os.path.join("src", html), "rt", encoding="utf8") as htmlfile:
            lines = htmlfile.read()
            print(lines)
            break


if __name__ == "__main__":
    os.remove(os.path.join("packs", "spells.db"))
    main()
