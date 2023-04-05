Hooks.once("ready", async () => {
    const compendium = await game.packs.get("5e-wikidot.spells");
    await compendium.configure( {"locked": false });
    const index = await compendium.getIndex();

    let response = await fetch("./modules/5e-wikidot/public/spells.json");
    let spellList = await response.json();

    for (let x = 0; x < spellList.length; x++) {
        let s = spellList[x];
        console.log(s);
        let response = await fetch("./modules/5e-wikidot/" + s);
        let data = await response.json();

        const i = index.find(i => i.name === data.name);

        if (!i) {
            const S = await Item.create(data, {temporary: true});
            await compendium.importDocument(S);
        }
    }
    await compendium.configure( {"locked": true });
})