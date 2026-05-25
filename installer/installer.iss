[Setup]
AppName=Tally Auto Rename
AppVersion=1.0
AppPublisher=Khushal Jain

DefaultDirName={localappdata}\TallyAutoRename
DefaultGroupName=Tally Auto Rename

OutputDir=.
OutputBaseFilename=TallyAutoRenameSetup

Compression=lzma
SolidCompression=yes

WizardStyle=modern

DisableProgramGroupPage=yes

; =====================================================
; REQUIRE ADMIN RIGHTS
; =====================================================

PrivilegesRequired=admin

UninstallDisplayIcon={app}\TallyRename.exe

; =====================================================
; FILES
; =====================================================

[Files]

Source: "C:\Users\User\Desktop\python khushal\FINAL 1.0\dist\sale purchase ledger copy.exe"; \
DestDir: "{app}"; \
DestName: "TallyRename.exe"; \
Flags: ignoreversion

; =====================================================
; SHORTCUTS
; =====================================================

[Icons]

Name: "{group}\Tally Auto Rename"; \
Filename: "{app}\TallyRename.exe"

Name: "{commondesktop}\Tally Auto Rename"; \
Filename: "{app}\TallyRename.exe"

Name: "{userstartup}\Tally Auto Rename"; \
Filename: "{app}\TallyRename.exe"

; =====================================================
; RUN AFTER INSTALL
; =====================================================

[Run]

Filename: "{app}\TallyRename.exe"; \
Description: "Launch Tally Auto Rename"; \
Flags: nowait postinstall skipifsilent

; =====================================================
; CUSTOM WATCH FOLDER PAGE
; =====================================================

[Code]

var
  WatchFolderPage: TInputDirWizardPage;

procedure InitializeWizard;
begin

  WatchFolderPage :=
    CreateInputDirPage(
      wpSelectDir,
      'Watch Folder',
      'Select Tally Export Folder',
      'Choose the folder where Tally exports PDFs.',
      False,
      ''
    );

  WatchFolderPage.Add('');

  WatchFolderPage.Values[0] :=
    'C:\tallydownloads';

end;

procedure CurStepChanged(CurStep: TSetupStep);

var
  ConfigText: string;
  ConfigPath: string;
  EscapedPath: string;

begin

  if CurStep = ssPostInstall then
  begin

    ConfigPath :=
      ExpandConstant('{app}\config.json');

    EscapedPath :=
      WatchFolderPage.Values[0];

    StringChangeEx(
      EscapedPath,
      '\',
      '\\',
      True
    );

    ConfigText :=
      '{'#13#10 +
      '    "watch_folder": "' +
      EscapedPath +
      '"'#13#10 +
      '}';

    SaveStringToFile(
      ConfigPath,
      ConfigText,
      False
    );

  end;

end;