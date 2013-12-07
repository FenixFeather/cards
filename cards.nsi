;NSIS Modern User Interface
;Basic Example Script
;Written by Joost Verburg

;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"

;--------------------------------
;General

  ;Name and file
  Name "Cards to Cards"
  OutFile "cards-1.4.3-win32-installer.exe"

  ;Default installation folder
  InstallDir "$PROGRAMFILES\Cards"
  
  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\Cards" ""

  ;Request application privileges for Windows Vista
  RequestExecutionLevel admin
  
;======================================================
; Defines
!define srcdir "./cards-1.4.3-win32"
!define productname "Cards to Cards"
!define regkey "Software\${productname}"
!define exec "cards_gui_client.exe"
!define uninstexec "Uninstall Cards.exe"
!define uninstkey "Software\Microsoft\Windows\CurrentVersion\Uninstall\${productname}"

;--------------------------------
;Variables

  Var StartMenuFolder
  
  
;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages
  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "${srcdir}\LICENSE"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  
  ;Start Menu Folder Page Configuration
  !define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU" 
  !define MUI_STARTMENUPAGE_REGISTRY_KEY "${regkey}" 
  !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
  
  !insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder
  
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH
  
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  
;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "Cards Core" SecDummy

  SetOutPath "$INSTDIR"
  
  ;ADD YOUR OWN FILES HERE...
  !include "files.nsi"
  File /a "${srcdir}\${exec}"
  
  ;Store installation folder
  WriteRegStr HKCU "${regkey}" "Install_Dir" "$INSTDIR"
  ; write uninstall strings
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${productname}" "DisplayName" "${productname} (remove only)"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${productname}" "UninstallString" '"$INSTDIR\${uninstexec}"'
  
  ;Create uninstaller
  WriteUninstaller "$INSTDIR\${uninstexec}"
  
  
!insertmacro MUI_STARTMENU_WRITE_BEGIN Application
  CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
  CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Cards to Cards GUI Client.lnk" "$INSTDIR\${exec}"
  CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Cards to Cards Server.lnk" "$INSTDIR\cards_server.exe"
  CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Cards to Cards Console Client.lnk" "$INSTDIR\cards_client.exe"
  CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\${uninstexec}"
!insertmacro MUI_STARTMENU_WRITE_END


SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecDummy ${LANG_ENGLISH} "Install main Cards files"

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDummy} $(DESC_SecDummy)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END
  

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ;ADD YOUR OWN FILES HERE...
  !include unfiles.nsi
  Delete "$INSTDIR\${exec}"
  
  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
    
  Delete "$SMPROGRAMS\$StartMenuFolder\Cards to Cards GUI Client.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\Cards to Cards Server.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\Cards to Cards Console Client.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
  RMDir "$SMPROGRAMS\$StartMenuFolder"

  Delete "$INSTDIR\${uninstexec}"

  RMDir "$INSTDIR"
  
  DeleteRegKey HKCU "${uninstkey}"
  DeleteRegKey HKCU "${regkey}"

SectionEnd
