"""Exercise the actual reset handler against a minimal core stub."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class TalentCommandTest(unittest.TestCase):
    def test_command(self):
        guard = Path('/home/aaron/Documents/ChatGPT/wow private server/scripts/wow-build-host-guard')
        subprocess.run([str(guard)], check=True)
        text = (ROOT / 'src/TalentButton.cpp').read_text()
        registration = text[text.index('TalentButtonCommandScript::GetCommands'):text.index('bool TalentButtonCommandScript::HandleModTalentResetCommand')]
        self.assertIn('Acore::ChatCommands::Console::No', registration)
        start = text.index('bool TalentButtonCommandScript::HandleModTalentResetCommand')
        end = text.index('\nvoid AddTalentButtonScripts()', start)
        source = r'''
#include <optional>
using std::optional;
template<class T> using Optional=optional<T>;
struct Player { int level=10, reset=0, pet=0, info=0; int GetLevel(){return level;}
 void resetTalents(bool){++reset;} void ResetPetTalents(){++pet;} void SendTalentsInfoData(bool){++info;} };
struct Session { Player* player; Player* GetPlayer(){return player;} };
struct ChatHandler { Session* session; int messages=0; Session* GetSession(){return session;} void PSendSysMessage(char const*){++messages;} };
namespace Acore::ChatCommands { struct PlayerIdentifier { Player* player; Player* GetConnectedPlayer(){return player;} }; }
struct Config { bool enabled=true; template<class T> T GetOption(char const*,T){return enabled;} } config;
Config* sConfigMgr=&config;
struct TalentButtonCommandScript {
 static bool HandleModTalentResetCommand(ChatHandler*,Optional<Acore::ChatCommands::PlayerIdentifier>);
 static bool CanUseCommand(Player*,ChatHandler*);
};
''' + text[start:end] + r'''
int main(){
 using I=Acore::ChatCommands::PlayerIdentifier; Player self,other; Session live{&self},empty{nullptr}; ChatHandler h{&live}, noSession{nullptr},noPlayer{&empty};
 if(TalentButtonCommandScript::HandleModTalentResetCommand(&noSession,{}) || TalentButtonCommandScript::HandleModTalentResetCommand(&noPlayer,{})) return 1;
 if(TalentButtonCommandScript::HandleModTalentResetCommand(&h,I{nullptr}) || TalentButtonCommandScript::HandleModTalentResetCommand(&h,I{&other})) return 2;
 if(TalentButtonCommandScript::CanUseCommand(nullptr,&h)) return 3;
 config.enabled=false; if(TalentButtonCommandScript::HandleModTalentResetCommand(&h,{})) return 4;
 config.enabled=true; self.level=9; if(TalentButtonCommandScript::HandleModTalentResetCommand(&h,{})) return 5;
 self.level=10; if(!TalentButtonCommandScript::HandleModTalentResetCommand(&h,{}) || self.reset!=1 || self.pet!=1 || self.info!=1 || h.messages!=1) return 6;
 if(!TalentButtonCommandScript::HandleModTalentResetCommand(&h,I{&self}) || self.reset!=2 || other.reset!=0) return 7;
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as directory:
            cpp = Path(directory) / 'command.cpp'
            cpp.write_text(source)
            binary = Path(directory) / 'command'
            subprocess.run(['g++', '-std=c++17', str(cpp), '-o', str(binary)], check=True)
            subprocess.run([str(binary)], check=True)

if __name__ == '__main__':
    unittest.main()
