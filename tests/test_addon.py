from pathlib import Path
import sys
import unittest
import zipfile
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import package

MOCK = '''
queue = {}; combat = false; SlashCmdList = {}
function InCombatLockdown() return combat end
C_Timer = {After = function(_, f) table.insert(queue, f) end}
function flush()
    local count = 0
    while #queue > 0 do
        count = count + 1; assert(count < 30, 'timer loop')
        table.remove(queue, 1)()
    end
end
function frame(alpha)
    local f = {alpha = alpha or 1, shown = true, hooks = {}, scripts = {}}
    function f:GetAlpha() return self.alpha end
    function f:SetAlpha(a) assert(not combat); self.alpha = a end
    function f:IsShown() return self.shown end
    function f:RegisterEvent() end
    function f:SetScript(k, fn) self.scripts[k] = fn end
    function f:HookScript(k, fn)
        self.hooks[k] = self.hooks[k] or {}; table.insert(self.hooks[k], fn)
    end
    function f:fire(k) for _, fn in ipairs(self.hooks[k] or {}) do fn(self) end end
    function f:Show() self.shown = true; self:fire('OnShow') end
    function f:Hide() self.shown = false; self:fire('OnHide') end
    return f
end
function CreateFrame() events = frame(); return events end
function hooksecurefunc(f, key, fn)
    local old = f[key]
    f[key] = function(...) old(...); fn(...) end
end
function event(name, arg) events.scripts.OnEvent(events, name, arg); flush() end
ObjectiveTrackerFrame = frame(0.8)
GamepadHudMode = frame(); GamepadHudMode.shown = false
'''

class AddonTests(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime()
        self.lua.execute(MOCK)
        self.lua.execute((ROOT / 'ForeverQuestHider/Core.lua').read_text(), 'ForeverQuestHider')

    def runlua(self, code):
        self.lua.execute(code)

    def test_defaults_and_reassert_without_hiding_frame(self):
        self.runlua("""
        event('ADDON_LOADED', 'Unrelated'); assert(ObjectiveTrackerFrame.alpha == 0.8)
        event('ADDON_LOADED', 'ForeverQuestHider')
        assert(ForeverQuestHiderDB.enabled and ObjectiveTrackerFrame.alpha == 0)
        assert(ObjectiveTrackerFrame:IsShown())
        ObjectiveTrackerFrame:SetAlpha(1); flush(); assert(ObjectiveTrackerFrame.alpha == 0)
        ObjectiveTrackerFrame:Show(); flush(); assert(ObjectiveTrackerFrame.alpha == 0)
        """)

    def test_hud_reveal_and_restore(self):
        self.runlua("""
        event('ADDON_LOADED', 'ForeverQuestHider')
        GamepadHudMode:Show(); flush(); assert(ObjectiveTrackerFrame.alpha == 0.8)
        GamepadHudMode:Hide(); flush(); assert(ObjectiveTrackerFrame.alpha == 0)
        SlashCmdList.FOREVERQUESTHIDER('off'); flush()
        assert(ObjectiveTrackerFrame.alpha == 0.8 and not ForeverQuestHiderDB.enabled)
        GamepadHudMode:Show(); flush(); GamepadHudMode:Hide(); flush()
        assert(ObjectiveTrackerFrame.alpha == 0.8)
        """)

    def test_combat_deferral_and_final_requested_state(self):
        self.runlua("""
        event('ADDON_LOADED', 'ForeverQuestHider'); combat = true
        SlashCmdList.FOREVERQUESTHIDER('off'); flush()
        assert(ObjectiveTrackerFrame.alpha == 0)
        combat = false; event('PLAYER_REGEN_ENABLED'); assert(ObjectiveTrackerFrame.alpha == 0.8)
        combat = true; SlashCmdList.FOREVERQUESTHIDER('on'); flush()
        SlashCmdList.FOREVERQUESTHIDER('off'); flush()
        combat = false; event('PLAYER_REGEN_ENABLED'); assert(ObjectiveTrackerFrame.alpha == 0.8)
        """)

    def test_saved_disabled_and_toggle(self):
        self.runlua("""
        ForeverQuestHiderDB = {enabled = false}
        event('ADDON_LOADED', 'ForeverQuestHider'); assert(ObjectiveTrackerFrame.alpha == 0.8)
        SlashCmdList.FOREVERQUESTHIDER(''); flush(); assert(ObjectiveTrackerFrame.alpha == 0)
        SlashCmdList.FOREVERQUESTHIDER('status'); flush(); assert(ObjectiveTrackerFrame.alpha == 0)
        SlashCmdList.FOREVERQUESTHIDER('nonsense'); flush(); assert(ObjectiveTrackerFrame.alpha == 0)
        """)

    def test_late_frames_and_coalescing(self):
        self.runlua("""
        local t, h = ObjectiveTrackerFrame, GamepadHudMode
        ObjectiveTrackerFrame = nil; GamepadHudMode = nil
        event('ADDON_LOADED', 'ForeverQuestHider')
        ObjectiveTrackerFrame = t; GamepadHudMode = h
        event('ADDON_LOADED', 'Blizzard_Gamepad')
        assert(t.alpha == 0)
        for i=1,100 do events.Schedule() end
        assert(#queue == 1); flush()
        h:Show(); flush(); assert(t.alpha == 0.8)
        """)

    def test_invalid_saved_state_and_combat_login(self):
        self.runlua("""
        ForeverQuestHiderDB = 'bad'; combat = true
        event('ADDON_LOADED', 'ForeverQuestHider'); assert(ObjectiveTrackerFrame.alpha == 0.8)
        combat = false; event('PLAYER_REGEN_ENABLED'); assert(ObjectiveTrackerFrame.alpha == 0)
        """)

class PackageTests(unittest.TestCase):
    def test_archive_and_version(self):
        with zipfile.ZipFile(package.package('v' + package.version())) as z:
            self.assertEqual(set(z.namelist()), {
                'ForeverQuestHider/ForeverQuestHider.toc', 'ForeverQuestHider/Core.lua',
                'ForeverQuestHider/LICENSE', 'ForeverQuestHider/README.md'})
            self.assertIn('## Interface: 16001', z.read('ForeverQuestHider/ForeverQuestHider.toc').decode())
        with self.assertRaises(ValueError):
            package.package('v9.9.9')

if __name__ == '__main__':
    unittest.main()
