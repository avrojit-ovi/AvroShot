; Inno Setup script for AvroShot - produces the installable AvroShot-Setup.exe
; Compile with: ISCC.exe avroshot.iss   (or run build_windows.bat)
;
; The installer performs a real, permanent install:
;   * "Install for all users" puts AvroShot in Program Files and registers it
;     for every account on the PC (needs admin approval once).
;   * "Install for me only" puts it in %LOCALAPPDATA%\Programs (no admin).
; Either way it gets a Start Menu entry, an optional Desktop shortcut, a
; standard Add/Remove Programs entry, and a working uninstaller.

#define AppName "AvroShot"
#define AppVersion "1.0.0"
#define AppPublisher "AvroShot Project"
#define AppExeName "AvroShot.exe"
#define AppUrl "https://github.com/avrojit-ovi/AvroShot"

[Setup]
AppId={{8E2B4A7F-3C51-4D2A-9B6E-AVROSHOT0001}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppUrl}
AppSupportURL={#AppUrl}/issues
AppUpdatesURL={#AppUrl}/releases
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
UninstallDisplayName={#AppName} {#AppVersion}
UninstallDisplayIcon={app}\{#AppExeName}
LicenseFile=..\LICENSE
OutputBaseFilename=AvroShot-Setup
OutputDir=..\dist
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
; Per-user by default; the user can choose "Install for all users" on the
; Select Setup Install Mode page to get a permanent machine-wide install.
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=icon.ico
CloseApplications=yes
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} Setup
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}
VersionInfoCopyright=MIT License
VersionInfoOriginalFileName=AvroShot-Setup.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\AvroShot.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\linux\assets\avroshot.svg"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Comment: "Capture and annotate your screen"
Name: "{group}\{#AppName} Settings"; Filename: "{app}\{#AppExeName}"; Parameters: "--settings"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
