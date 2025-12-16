print("This script is running inside the Astroluma sandbox!")
print("_G is:")
printtable(_G)
print("_VERSION is:".._VERSION)

events.registerNewEvent("communicate",1)

function events.init()
	print("Sandbox init.")
	events:fire("communicate","Absolute Cinema")
	print("Bwuh")
end
shared.test = 54