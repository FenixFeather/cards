File /a "${srcdir}\*.pyd"
File /a "${srcdir}\*.dll"
File /a "${srcdir}\*.zip"
File /a "${srcdir}\*.txt"
File /a "${srcdir}\*.ini"
File /a "${srcdir}\*.md"
File /a "${srcdir}\CHANGELOG"
File /a "${srcdir}\LICENSE"
AccessControl::GrantOnFile \
    "$INSTDIR\settings.ini" "(S-1-5-32-545)" "GenericRead + GenericWrite"
File /r "${srcdir}\img"
; File "${srcdir}\logs"
AccessControl::GrantOnFile \
    "$INSTDIR" "(S-1-5-32-545)" "GenericRead + GenericWrite"
