function(code,env)
    env._G = env
    local fn,err = load(code,"sandbox","t",env)
    if not fn then
        return false, err
    end
    local success, result = xpcall(fn, debug.traceback)
    return success,result
end