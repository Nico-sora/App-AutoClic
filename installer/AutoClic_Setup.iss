; AutoClic Installer Script — Inno Setup 6+

[Setup]
AppName=AutoClic
AppVersion=1.0
AppPublisher=AutoClic Gz
AppPublisherURL=https://github.com/AutoClic
DefaultDirName={autopf}\AutoClic Gz
DefaultGroupName=AutoClic Gz
OutputDir=..\dist
OutputBaseFilename=AutoClic_Setup
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\AutoClic.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64compatible
DisableWelcomePage=no
LicenseFile=
WizardImageFile=
WizardSmallImageFile=

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"

[CustomMessages]
spanish.StartMenuIcon=Crear acceso directo en el Menu Inicio
english.StartMenuIcon=Create Start Menu shortcut
portuguese.StartMenuIcon=Criar atalho no Menu Iniciar
french.StartMenuIcon=Creer un raccourci dans le Menu Demarrer
german.StartMenuIcon=Startmenu-Verknupfung erstellen
italian.StartMenuIcon=Crea collegamento nel Menu Start
russian.StartMenuIcon=Создать ярлык в меню Пуск
japanese.StartMenuIcon=スタートメニューにショートカットを作成
korean.StartMenuIcon=시작 메뉴에 바로가기 만들기
polish.StartMenuIcon=Utworz skrot w Menu Start
turkish.StartMenuIcon=Baslat Menusu kisayolu olustur
dutch.StartMenuIcon=Snelkoppeling in Startmenu maken
arabic.StartMenuIcon=إنشاء اختصار في قائمة ابدأ
spanish.LaunchNow=Ejecutar AutoClic ahora
english.LaunchNow=Launch AutoClic now
portuguese.LaunchNow=Executar AutoClic agora
french.LaunchNow=Lancer AutoClic maintenant
german.LaunchNow=AutoClic jetzt starten
italian.LaunchNow=Avvia AutoClic ora
russian.LaunchNow=Запустить AutoClic сейчас
japanese.LaunchNow=今すぐAutoClicを起動
korean.LaunchNow=지금 AutoClic 실행
polish.LaunchNow=Uruchom AutoClic teraz
turkish.LaunchNow=AutoClic'i simdi baslat
dutch.LaunchNow=AutoClic nu starten
arabic.LaunchNow=تشغيل AutoClic الآن

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "startmenu"; Description: "{cm:StartMenuIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
Source: "..\dist\AutoClic.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Desktop shortcut
Name: "{autodesktop}\AutoClic"; Filename: "{app}\AutoClic.exe"; IconFilename: "{app}\AutoClic.exe"; Tasks: desktopicon
; Start Menu shortcut
Name: "{group}\AutoClic"; Filename: "{app}\AutoClic.exe"; IconFilename: "{app}\AutoClic.exe"; Tasks: startmenu
Name: "{group}\Desinstalar AutoClic"; Filename: "{uninstallexe}"; Tasks: startmenu

[Run]
Filename: "{app}\AutoClic.exe"; Description: "{cm:LaunchNow}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  Lang: String;
  ConfigDir: String;
  ConfigPath: String;
  ActiveLang: String;
begin
  if CurStep = ssPostInstall then
  begin
    ActiveLang := ActiveLanguage;

    if ActiveLang = 'spanish' then Lang := 'es'
    else if ActiveLang = 'english' then Lang := 'en'
    else if ActiveLang = 'portuguese' then Lang := 'pt'
    else if ActiveLang = 'french' then Lang := 'fr'
    else if ActiveLang = 'german' then Lang := 'de'
    else if ActiveLang = 'italian' then Lang := 'it'
    else if ActiveLang = 'russian' then Lang := 'ru'
    else if ActiveLang = 'japanese' then Lang := 'ja'
    else if ActiveLang = 'korean' then Lang := 'ko'
    else if ActiveLang = 'polish' then Lang := 'pl'
    else if ActiveLang = 'turkish' then Lang := 'tr'
    else if ActiveLang = 'dutch' then Lang := 'nl'
    else if ActiveLang = 'arabic' then Lang := 'ar'
    else Lang := 'en';

    ConfigDir := ExpandConstant('{userappdata}\AutoClic Gz');
    ForceDirectories(ConfigDir);
    ConfigPath := ConfigDir + '\config.json';

    // Only create if no config exists yet (don't overwrite user settings on reinstall)
    if not FileExists(ConfigPath) then
      SaveStringToFile(ConfigPath,
        '{' + #13#10 +
        '  "language": "' + Lang + '"' + #13#10 +
        '}', False);
  end;
end;

[UninstallDelete]
; User data lives in %APPDATA%\AutoClic Gz
Type: files; Name: "{userappdata}\AutoClic Gz\config.json"
Type: files; Name: "{userappdata}\AutoClic Gz\session_log.json"
Type: filesandordirs; Name: "{userappdata}\AutoClic Gz\profiles"
Type: dirifempty; Name: "{userappdata}\AutoClic Gz"
