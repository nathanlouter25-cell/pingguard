; PingGuard Inno Setup Script
; Wraps dist\PingGuard.exe and optional assets
; Build with: ISCC.exe PingGuard_Setup.iss

#define AppName      "PingGuard"
#define AppVersion   "1.4"
#define AppPublisher "PingGuard"
#define AppURL       "https://pingguard.itch.io"
#define AppExeName   "PingGuard.exe"
#define AppMutex     "PingGuardSingleInstance_47823"

; ─────────────────────────────────────────────────────────────────
[Setup]
AppId                    = {{A7F3C2D1-8B4E-4F9A-B6D2-3E1C5A7F9B8D}
AppName                  = {#AppName}
AppVersion               = {#AppVersion}
AppVerName               = {#AppName} v{#AppVersion}
AppPublisher             = {#AppPublisher}
AppPublisherURL          = {#AppURL}
AppSupportURL            = {#AppURL}
AppUpdatesURL            = {#AppURL}
AppMutex                 = {#AppMutex}

; Install into Program Files\PingGuard by default
DefaultDirName           = {autopf}\{#AppName}
DefaultGroupName         = {#AppName}
DisableProgramGroupPage  = yes

; Output
OutputDir                = installer_output
OutputBaseFilename       = PingGuard_Setup_v{#AppVersion}
SetupIconFile            = assets\icon.ico

; Compression
Compression              = lzma2/ultra64
SolidCompression         = yes
LZMAUseSeparateProcess   = yes

; Appearance
WizardStyle              = modern
WizardSizePercent        = 120
DisableWelcomePage       = no

; Windows version requirement (Windows 10+)
MinVersion               = 10.0

; Don't require admin — installs per-user if not admin
PrivilegesRequiredOverridesAllowed = commandline dialog
PrivilegesRequired       = lowest

; Uninstaller
UninstallDisplayIcon     = {app}\{#AppExeName}
UninstallDisplayName     = {#AppName} v{#AppVersion}

; Restart Manager — close PingGuard if running before install/uninstall
CloseApplications        = yes
CloseApplicationsFilter  = {#AppExeName}
RestartApplications      = yes

; Architecture
ArchitecturesInstallIn64BitMode = x64compatible

; ─────────────────────────────────────────────────────────────────
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

; ─────────────────────────────────────────────────────────────────
[Tasks]
Name: "desktopicon";  Description: "Create a &desktop shortcut";   GroupDescription: "Additional icons:"; Flags: unchecked
Name: "startupentry"; Description: "Launch PingGuard at &Windows startup"; GroupDescription: "Startup:"; Flags: unchecked

; ─────────────────────────────────────────────────────────────────
[Files]
; Main executable (PyInstaller one-file build)
Source: "dist\{#AppExeName}";  DestDir: "{app}"; Flags: ignoreversion

; App icon (used by shortcuts)
Source: "assets\icon.ico";     DestDir: "{app}\assets"; Flags: ignoreversion

; Optional: any extra assets bundled separately (sounds, etc.)
; Source: "assets\*";          DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs

; ─────────────────────────────────────────────────────────────────
[Icons]
; Start Menu shortcut
Name: "{group}\{#AppName}";            Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\assets\icon.ico"
Name: "{group}\Uninstall {#AppName}";  Filename: "{uninstallexe}"

; Desktop shortcut (optional task)
Name: "{autodesktop}\{#AppName}";      Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\assets\icon.ico"; Tasks: desktopicon

; ─────────────────────────────────────────────────────────────────
[Registry]
; Windows startup entry (optional task — mirrors what the app does itself)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
  ValueType: string; ValueName: "{#AppName}"; \
  ValueData: """{app}\{#AppExeName}"""; \
  Flags: uninsdeletevalue; Tasks: startupentry

; ─────────────────────────────────────────────────────────────────
[Run]
; Launch after install (not as admin — so tray works correctly)
Filename: "{app}\{#AppExeName}"; \
  Description: "Launch {#AppName} now"; \
  Flags: nowait postinstall skipifsilent runasoriginaluser

; ─────────────────────────────────────────────────────────────────
[UninstallRun]
; Kill the running process before uninstalling
Filename: "taskkill.exe"; Parameters: "/F /IM {#AppExeName}"; \
  Flags: runhidden skipifdoesntexist; RunOnceId: "KillPingGuard"

; ─────────────────────────────────────────────────────────────────
[UninstallDelete]
; Clean up settings/logs left behind in AppData
Type: filesandordirs; Name: "{localappdata}\{#AppName}"
Type: filesandordirs; Name: "{userappdata}\{#AppName}"

; ─────────────────────────────────────────────────────────────────
[Code]
{ ── Prevent running the installer while PingGuard is open ── }
function InitializeSetup(): Boolean;
var
  Msg: String;
begin
  Result := True;
  if CheckForMutexes('{#AppMutex}') then
  begin
    Msg := '{#AppName} is currently running.' + #13#10 +
           'Please close it from the system tray before installing.';
    MsgBox(Msg, mbError, MB_OK);
    Result := False;
  end;
end;

{ ── Remove old startup registry key on uninstall if app didn't ── }
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    RegDeleteValue(HKEY_CURRENT_USER,
      'Software\Microsoft\Windows\CurrentVersion\Run',
      '{#AppName}');
  end;
end;
