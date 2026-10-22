; Inno Setup script for AvroShot - produces AvroShot-Setup.exe
; Compile with: ISCC.exe avroshot.iss   (or run build_windows.bat)

#define AppName "AvroShot"
#define AppVersion "1.0.0"
#define AppPublisher "AvroShot Project"
#define AppExeName "AvroShot.exe"

[Setup]
AppId={{8E2B4A7F-3C51-4D2A-9B6E-AVROSHOT0001}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}
OutputBaseFilename=AvroShot-Setup
OutputDir=..\dist
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=icon.ico
CloseApplications=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\AvroShot.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\linux\assets\avroshot.svg"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{#AppName} Settings"; Filename: "{app}\{#AppExeName}"; Parameters: "--settings"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
