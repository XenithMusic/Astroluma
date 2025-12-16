print("Second script")
function events.init()
	-- body
end
function events.preinit()
	events.registerNewEvent("communicate",1)
	function events.communicate(a)
		print("COMMUNICATE EVENT QSDHWHFE")
		print(_CONTEXT,"recieving",a)
	end
	print("AAAA")
end
if python.contains(shared,"test") then
	print(shared.test)
else
	error("Test does not exist for some reason.")
end