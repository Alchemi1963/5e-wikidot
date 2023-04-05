import json
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
	             components, concentration=False, ritual=False, scaling = None, save = None):
		self._id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
		self.name = name
		self.ownership = {"default": 0}
		self.type = "spell"

		self.system = {}
		self.system["description"] = {}
		self.system["description"]["value"] = desc.replace("\n", "<br>")
		self.system["description"]["chat"] = None
		self.system["description"]["unidentified"] = None
		self.system["source"] = source

		self.system["activation"] = {}
		self.system["activation"]["type"] = casting_time[1]
		self.system["activation"]["cost"] = int(casting_time[0])
		self.system["activation"]["condition"] = None

		self.system["duration"] = {}
		self.system["duration"]["value"] = duration[0]
		self.system["duration"]["units"] = duration[1]
		self.system["cover"] = None

		self.system["target"] = {}
		self.system["target"]["value"] = target[0]
		self.system["target"]["width"] = None
		self.system["target"]["units"] = target[2]
		self.system["target"]["type"] = target[1]

		self.system["range"] = {}
		self.system["range"]["value"] = sp_range[0]
		self.system["range"]["long"] = None
		self.system["range"]["units"] = sp_range[1]

		self.system["uses"] = {}
		self.system["uses"]["value"] = None
		self.system["uses"]["max"] = None
		self.system["uses"]["per"] = None
		self.system["uses"]["recovery"] = None

		self.system["consume"] = {}
		self.system["consume"]["type"] = None
		self.system["consume"]["target"] = None
		self.system["consume"]["amount"] = None

		self.system["ability"] = None
		self.system["actionType"] = action_type
		self.system["attackBonus"] = None
		self.system["chatFlavor"] = None

		self.system["critical"] = {}
		self.system["critical"]["threshold"] = None
		self.system["critical"]["damage"] = None

		self.system["damage"] = {}
		self.system["damage"]["parts"] = []

		match = re.search("(\\d+d\\d+ (?:\\+ your spellcasting ability modifier )?\\w+) damage", desc)
		if match:
			for group in match.groups():
				group = group.replace(" + your spellcasting ability modifier", "+@mod")
				self.system["damage"]["parts"].append(group.split(" "))
		else:
			match = re.search("(?:(?:heal )|(?:hit points? equal to ))(\\d+d\\d+) ?(?:\\+ your spellcasting ability modifier)?", desc)
			if match and not "temporary" in desc:
				self.system["damage"]["parts"].append((match.group(1), "healing"))
			elif match:
				self.system["damage"]["parts"].append((match.group(1), "temphp"))

		self.system["damage"]["versatile"] = None

		self.system["formula"] = None

		self.system["save"] = {}
		self.system["save"]["ability"] = save
		self.system["save"]["dc"] = None
		self.system["save"]["scaling"] = "spell"

		self.system["level"] = level
		self.system["school"] = school

		self.system["components"] = {}
		self.system["components"]["vocal"] = "V" in components
		self.system["components"]["somatic"] = "S" in components
		self.system["components"]["material"] = "M" in components
		self.system["components"]["ritual"] = ritual
		self.system["components"]["concentration"] = concentration

		self.system["materials"] = {}
		if self.system["components"]["material"]:
			self.system["materials"]["value"] = re.search(".+\\((.+)\\)", components).group(1)
			self.system["materials"]["consumed"] = "consume" in components
			match = re.search(".+(\\d+)GP", components)
			if match:
				self.system["materials"]["cost"] = match.group(1)
			else:
				self.system["materials"]["cost"] = None
		else:
			self.system["materials"]["value"] = None
			self.system["materials"]["consumed"] = False
			self.system["materials"]["cost"] = None
		self.system["materials"]["supply"] = 0

		self.system["preparation"] = {}
		self.system["preparation"]["mode"] = "prepared"
		self.system["preparation"]["prepared"] = "false"

		self.system["scaling"] = {}
		self.system["scaling"]["mode"] = scaling[1]
		self.system["scaling"]["formula"] = scaling[0]

		self.sort = 0
		self.flags = {}
		self.img = "icons/svg/fire-shield.svg"
		self.effects = []
		self.folder = None

		self._stats = {"systemId": "dnd5e", "systemVersion": "2.1.0", "coreVersion": "10.291"}

		self.writeToFile()

	def __str__(self):
		return json.dumps(
			{"_id": self._id, "name": self.name, "ownership": self.ownership, "type": self.type, "system": self.system,
			 "sort": self.sort, "flags": self.flags, "img": self.img, "effects": self.effects, "folder": self.folder,
			 "_stats": self._stats}, ensure_ascii=False).encode("utf8").decode()

	def writeToFile(self):
		if not os.path.exists("src"):
			os.mkdir("src")
		else:
			writeDir = ""
			if self.system["level"] == 0:
				writeDir = "cantrips"
			else:
				writeDir = f"level-{self.system['level']}"

			writeDir = os.path.join("src", "spells", writeDir)
			if not os.path.exists(writeDir):
				os.makedirs(writeDir, exist_ok=True)

			with open(os.path.join(writeDir, f"{self.name.replace(' ', '-').replace('/', '-').replace(os.path.sep, '-').lower()}.json"), "wt", encoding="utf8") as f:
				f.write(self.__str__())

def main():
	for html in os.listdir("src"):
		if not html.endswith(".html"):
			continue

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
					school = school.strip()[:3]

				ca_value = p_ca_value.search(sp).group(1)
				ca_units = p_ca_units.search(sp).group(1)

				sp_range = p_range.search(sp).group(1)

				target = [None, None, "ft"]  # value type units
				spell_range = [None, None]  # value units

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
						dur = [None, "inst"]
					elif "Duration:</strong> Until dispelled" in sp:
						dur = [None, "perm"]
					elif "Duration:</strong> Special" in sp:
						dur = [None, "spec"]
				dur = (dur[0], re.sub("(\\w+)s", "\\1", dur[1]))

				desc = p_descr.search(sp).group(1)

				if "self" == sp_range.lower():
					spell_range[1] = "self"
					target[1] = "self"
					target[2] = None

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

				if spell_range[1] == "feet" or spell_range[1] == "foot":
					spell_range[1] = "ft"

				scaling = [None, None]

				if "at higher levels" in sp.lower():
					match = re.search("(?:A|a)t (?:H|h)igher (?:L|l)evels.+</strong> .+increases by (\d+d\d+).+</p>", desc)
					if match:
						scaling[0] = match.group(1)
						if lvl == 0:
							scaling[1] = "cantrip"
						else:
							scaling[1] = "level"

				save = None
				if "saving throw" in desc:
					match = re.search("(\\w+) saving throw", desc)
					if match:
						match match.group(1).lower():
							case "strength":
								save = "str"
							case "dexterity":
								save = "dex"
							case "constitution":
								save = "con"
							case "intelligence":
								save = "int"
							case "wisdom":
								save = "wis"
							case "charisma":
								save = "cha"


				Spell(name, desc, src, (ca_value, ca_units), dur, target, spell_range, "spell", lvl, school, components,
				      concentration, ritual, scaling, save)

			except:
				print(html)
				print(traceback.format_exc())
			finally:
				print(f"{html} was parsed.")


if __name__ == "__main__":
	if os.path.exists(os.path.join("packs", "spells.db")):
		os.remove(os.path.join("packs", "spells.db"))
	main()
