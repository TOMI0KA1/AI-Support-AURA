; Inno Setup script template for Aura installer
[Setup]
AppName=Aura
AppVersion=1.0
DefaultDirName={pf}\Aura
DefaultGroupName=Aura
OutputDir=installer
OutputBaseFilename=AuraSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\Aura\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Aura"; Filename: "{app}\Aura.exe"
Name: "{commondesktop}\Aura"; Filename: "{app}\Aura.exe"
