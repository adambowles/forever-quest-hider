local addonName = ...
local events = CreateFrame("Frame")
local ready, queued, applying = false, false, false
local tracker, hud, originalAlpha
local function Enabled()
    return ForeverQuestHiderDB and ForeverQuestHiderDB.enabled
end
local function Navigating()
    return GamepadHudMode and GamepadHudMode:IsShown()
end
local function Apply()
    queued = false
    if not ready or InCombatLockdown() then return end
    local frame = ObjectiveTrackerFrame
    if not frame then return end
    if tracker ~= frame then
        tracker = frame
        originalAlpha = frame:GetAlpha()
        hooksecurefunc(frame, "SetAlpha", function()
            if not applying then events.Schedule() end
        end)
        frame:HookScript("OnShow", function() events.Schedule() end)
    end
    if GamepadHudMode and hud ~= GamepadHudMode then
        hud = GamepadHudMode
        hud:HookScript("OnShow", function() events.Schedule() end)
        hud:HookScript("OnHide", function() events.Schedule() end)
    end
    -- Keep the frame registered and available to Blizzard's controller navigation.
    -- Never hide/reparent it or replace its methods. Reveal it while HUD mode owns focus.
    applying = true
    frame:SetAlpha(Enabled() and not Navigating() and 0 or originalAlpha)
    applying = false
end
function events.Schedule()
    if not ready or queued then return end
    queued = true
    C_Timer.After(0, Apply)
end
events:RegisterEvent("ADDON_LOADED")
events:RegisterEvent("PLAYER_ENTERING_WORLD")
events:RegisterEvent("PLAYER_REGEN_ENABLED")
events:RegisterEvent("CVAR_UPDATE")
events:SetScript("OnEvent", function(_, event, name)
    if event == "ADDON_LOADED" and name == addonName then
        if type(ForeverQuestHiderDB) ~= "table" then ForeverQuestHiderDB = {} end
        if type(ForeverQuestHiderDB.enabled) ~= "boolean" then
            ForeverQuestHiderDB.enabled = true
        end
        ready = true
    end
    events.Schedule()
end)
SLASH_FOREVERQUESTHIDER1 = "/fth"
SlashCmdList.FOREVERQUESTHIDER = function(message)
    if not ready then return end
    local command = (message or ""):lower():match("^%s*(.-)%s*$")
    if command == "" or command == "toggle" then
        ForeverQuestHiderDB.enabled = not Enabled()
    elseif command == "on" or command == "hide" then
        ForeverQuestHiderDB.enabled = true
    elseif command == "off" or command == "show" then
        ForeverQuestHiderDB.enabled = false
    elseif command ~= "status" then
        print("Forever Quest Hider: /fth [on|off|toggle|status]")
        return
    end
    events.Schedule()
    print("Forever Quest Hider: " .. (Enabled() and "enabled" or "disabled")
        .. (InCombatLockdown() and " (applies after combat)" or ""))
end
