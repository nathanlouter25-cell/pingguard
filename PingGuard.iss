; PingGuard Inno Setup Installer Script
; Requires Inno Setup 6+ — https://jrsoftware.org/isinfo.php
; Build: Open this file in Inno Setup Compiler and click Compile (Ctrl+F9)

#define MyAppName "PingGuard"
#define MyAppVersion "2.0.3"
#define MyAppPublisher "Jackal Products"
#define MyAppURL "https://jackalproducts.itch.io/pingguard"
#define MyAppExeName "PingGuard.exe"
#define MySourceExe "dist\PingGuard.exe"
#define MyIconFile "assets\icon.ico"

[Setup]
AppId={{A3F7C2D1-88B4-4E6A-9F3D-512C8E4B7A90}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Install to Program Files
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output installer to project root
OutputDir=installer
OutputBaseFilename=PingGuard-Setup-{#MyAppVersion}

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; Appearance
WizardStyle=modern
WizardSizePercent=110
SetupIconFile={#MyIconFile}
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

; Permissions — install without needing admin if possible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Minimum Windows version: Windows 10
MinVersion=10.0

; Misc
ShowLanguageDialog=no
DisableWelcomePage=no
DisableReadyPage=no
DisableFinishedPage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
; Desktop shortcut (ticked by default)
Name: "desktopicon"; Description: "Create a &desktop shortcut"
; Run at startup (unticked by default — user can enable in Settings)
Name: "startup"; Description: "Start PingGuard with &Windows"

[Files]
; Main executable
Source: "{#MySourceExe}"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion

; App icon (for uninstall display)
Source: "{#MyIconFile}"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

; Desktop
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"; Tasks: desktopicon

; Startup (runs minimised to tray)
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--minimized"; Tasks: startup

[Run]
; Launch after install (checkbox on final page)
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up any leftover files in the install dir
Type: filesandordirs; Name: "{app}"

[Code]
// Close any running instance of PingGuard before install/uninstall
procedure CloseRunningInstance();
var
  ResultCode: Integer;
begin
  Exec('taskkill.exe', '/F /IM PingGuard.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
    CloseRunningInstance();
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
    CloseRunningInstance();
end;
