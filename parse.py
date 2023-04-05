import os
import random
import re
import string
import traceback

# format for db
# {"_id":"kKv7GwOuFovGUWtK","name":"Blade Ward","type":"spell","img":"icons/svg/fire-shield.svg","data":{"description":{"value":"<p>You extend your hand and trace a sigil of warding in the air. Until the end of your next turn, you have resistance against bludgeoning, piercing, and slashing damage dealt by weapon attacks.</p>","chat":"","unidentified":""},"source":"Player's Handbook","activation":{"type":"action","cost":1,"condition":""},"duration":{"value":1,"units":"round"},"target":{"value":null,"width":null,"units":"self","type":""},"range":{"value":null,"long":null,"units":"self"},"uses":{"value":null,"max":"","per":""},"consume":{"type":"","target":"","amount":null},"ability":"","actionType":"other","attackBonus":"0","chatFlavor":"","critical":{"threshold":null,"damage":""},"damage":{"parts":[["","bludgeoning"]],"versatile":""},"formula":"","save":{"ability":"","dc":null,"scaling":"spell"},"level":0,"school":"abj","components":{"value":"","vocal":true,"somatic":true,"material":false,"ritual":false,"concentration":false},"materials":{"value":"","consumed":false,"cost":0,"supply":0},"preparation":{"mode":"prepared","prepared":false},"scaling":{"mode":"none","formula":""}},"effects":[{"_id":"RL134Mwf7zbeWje3","changes":[{"key":"Bludgeoning","mode":1,"value":"0.5"},{"key":"Piercing","mode":1,"value":"0.5"},{"key":"Slashing","mode":1,"value":"0.5"}],"disabled":false,"duration":{"rounds":1,"startTime":0},"icon":"icons/svg/shield.svg","label":"Resistance","origin":"Item.b4427ysQc5erIPuZ","transfer":true,"flags":{},"tint":"#cc0000"}],"folder":null,"sort":0,"permission":{"default":0,"EbhaPUSsc0xE98gi":3},"flags":{"core":{"sourceId":"Item.b4427ysQc5erIPuZ"}}}

# re patterns
p_name = re.compile("page-title.+<span>(.+)</span>")
p_src = re.compile("Source: (.+)</p>")
p_lvl = re.compile("<em>(\\d+).+level.+</em>")
p_school = re.compile("<em>.+level (.+)</em>")
p_school_cantrip = re.compile("<em>(.+) cantrip.*</em>")
p_ca_value = re.compile("Casting Time:</strong> (\\d+)")
p_ca_units = re.compile("Casting Time:</strong> \\d+ (.+)<")
p_range = re.compile("Range:</strong> (.+)<")
p_components = re.compile("Components:</strong> (.+)<")
p_duration = re.compile("Duration:</strong> [A-z\\s]*(\\d+) (.+)<")
p_duration_concentration = re.compile("Duration:</strong> Concentration, [U|u]p to (\\d+) (.+)<")
p_descr = re.compile("Duration:.+</p>\\n([\\s\\S]+)<p><strong><em>")

# spell db
spells = []

newline = "\n"
empty = ""

class Spell:
	def __init__(self, name, desc, source, casting_time, duration, target, sp_range, action_type, level, school,
	             components, concentration=False, ritual=False):
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
		self.range_value = sp_range[0]
		self.range_units = sp_range[1]
		self.actionType = action_type  # rsak, msak, util, heal, save, other
		self.level = level
		self.school = school

		self.vocal = False
		self.somatic = False
		self.material = False
		self.mvalue = ""

		# components
		if "V" in components:
			self.vocal = True
		if "S" in components:
			self.somatic = True
		if "M" in components:
			self.material = True
			self.mvalue = re.sub(".+\\((.+)\\)", "\\1", components).strip()
		self.ritual = ritual
		self.concentration = concentration

		spells.append(self)

		self.saveToDB()

	def __str__(self):
		return f"Spell:\n" \
		       f"\tname:\t\t\t{self.name}\n" \
		       f"\tsource:\t\t\t{self.source}\n" \
		       f"\tlevel:\t\t\t{self.level}\n" \
		       f"\tschool:\t\t\t{self.school}\n" \
		       f"\tduration:\t\t{self.duration_value} {self.duration_units}\n" \
		       f"\tcomponents:\t\t{self.vocal, self.somatic, self.material, self.mvalue}\n" \
		       f"\tritual:\t\t\t{self.ritual}\n" \
		       f"\tconcentration:\t{self.concentration}\n" \
		       f"\tdescription\t\t{self.description}\n" \
		       f"\tactivation:\t\t{self.activation_cost} {self.activation_type}\n" \
		       f"\ttarget:\t\t\t{self.target_value} {self.target_type} {self.target_units}\n" \
		       f"\trange:\t\t\t{self.range_value} {self.range_units}\n" \
		       f"\tactionType:\t\t{self.actionType}"

	def saveToDB(self):
		if not os.path.exists("packs"):
			os.mkdir("packs")

		strs = f'{{"_id": {self._id},"name": {self.name},"type": "spell","img": {self.img},"data": {{"description": {{"value": {self.description},"chat": "","unidentified": ""}},"source": {self.source},"activation": {{"type": {self.activation_type},"cost": {self.activation_cost},"condition": ""}},"duration": {{"value": {self.duration_value},"units": {self.duration_units}}},"target": {{"value": {self.target_value},"width": null,"units": {self.target_units},"type": {self.target_type}}},"range": {{"value": {self.range_value},"long": null,"units": {self.range_units}}},"uses": {{"value": null,"max": "","per": ""}},"consume": {{"type": "","target": "","amount": null}},"ability": "","actionType": {self.actionType},"attackBonus": "0","chatFlavor": "","critical": {{"threshold": null,"damage": ""}},"damage": {{}},"formula": "","save": {{"ability": "","dc": null,"scaling": "spell"}},"level": {self.level},"school": {self.school},"components": {{"value": {self.mvalue},"vocal": {self.vocal},"somatic": {self.somatic},"material": {self.material},"ritual": {self.ritual},"concentration": {self.concentration}}},"materials": {{"value": {self.mvalue},"consumed": false,"cost": 0,"supply": 0}},"preparation": {{"mode": "prepared","prepared": false}},"scaling": {{"mode": "none","formula": ""}}}},"effects": [],"folder": null,"sort": 0,"permission": {{"default": 0}}}}'.replace("\n", "")

		print(strs)
		with open(os.path.join("packs", "spells.db"), "at", encoding="utf8") as db:
			db.write(strs)
			db.write("\n")


def main():
	for html in os.listdir("src"):
		with open(os.path.join("src", html), "rt", encoding="utf8") as htmlfile:
			try:
				sp = htmlfile.read()

				if "you want to access does not exist." in sp:
					continue

				name = p_name.search(sp).group(1)
				src = p_src.search(sp).group(1)
				if "cantrip" in sp.lower():
					lvl = 0
					school = p_school_cantrip.search(sp).group(1)
				else:
					lvl = p_lvl.search(sp).group(1)
					school = p_school.search(sp).group(1)
				if "(ritual)" in school.lower():
					ritual = True
				else:
					ritual = False

				if "transmutation" in school.lower():
					school = "trs"
				else:
					school = school[:2]

				ca_value = p_ca_value.search(sp).group(1)
				ca_units = p_ca_units.search(sp).group(1)

				sp_range = p_range.search(sp).group(1)

				target = ["null", "null", "ft"]  # value type units
				spell_range = ["null", "null"]  # value units

				components = p_components.search(sp).group(1)
				dur = p_duration_concentration.search(sp)
				if dur:
					dur = dur.groups()
					concentration = True
				else:
					concentration = False
					dur = p_duration.search(sp)
					if dur:
						dur = dur.groups()
					elif "Duration:</strong> Instant" in sp:
						dur = ["null", "inst"]
					elif "Duration:</strong> Until dispelled" in sp:
						dur = ["null", "perm"]
					elif "Duration:</strong> Special" in sp:
						dur = ["null", "spec"]
				dur = (dur[0], re.sub("(\\w+)s", "\\1", dur[1]))

				desc = p_descr.search(sp).group(1)

				if "self" == sp_range.lower():
					spell_range[1] = "self"
					target[1] = "self"
					target[2] = "null"

				elif "self" in sp_range.lower():
					target[0] = re.search("(\\d+)", sp_range).group(0)
					target[1] = re.search("\\d+.+[-\\s](\\w+)", sp_range).group(1)
					spell_range[1] = "self"

				else:
					match = re.search("(\\d+)-foot(?:-radius)?\\s(\\w+)", desc)
					if match:
						target[0] = match.group(1)
						target[1] = match.group(2)
						if target[1] == "radius":
							target[1] = "sphere"

					match = re.search("(\\d+)\\s(\\w+)", sp_range)
					if match:
						spell_range[0], spell_range[1] = match.groups()
					elif "touch" in sp_range.lower():
						spell_range[1] = "touch"

				Spell(name, desc, src, (ca_value, ca_units), dur, target, spell_range, "spell", lvl, school, components,
				      concentration, ritual)
			except:
				print(html)
				print(traceback.format_exc())
			finally:
				print(f"{html} was parsed.")


if __name__ == "__main__":
	if os.path.exists(os.path.join("packs", "spells.db")):
		os.remove(os.path.join("packs", "spells.db"))
	main()
