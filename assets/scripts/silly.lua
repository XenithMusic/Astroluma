if _CONTEXT[0] == "menu" then
    print("A")
    function init(shared)
        print("WHOA, IT WORKED!")
    end
    menu.register("gob",init)
    print("B")
    return
end
print(game.settings.get())
a = game.settings.get()
a.locale = "de_DE"
game.settings.set(a)
return game.assets.get("locale","de_DE")["keys"]["gui.menu.fire"]