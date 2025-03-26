from dataclasses import dataclass

@dataclass
class EpicData:

    # Token
    accessToken:str      = ""
    expiresIn:int        = 0
    expiresAt:str        = ""
    tokenType:str        = ""

    # Refresh
    refreshToken:str     = ""
    refreshExpires:str   = ""
    refreshExpiresAt:str = ""

    # IDs
    accountID:str        = ""
    clientID:str         = ""

    # Client
    internalClient:bool  = False
    clientService:str    = ""

    # Information
    displayName:str      = ""

    # App
    app:str              = ""
    appID:str            = ""

    def to_dict(self):
        return {
            "accessToken"      : self.accessToken,
            "expiresIn"        : self.expiresIn,
            "expiresAt"        : self.expiresAt,
            "tokenType"        : self.tokenType,
            "refreshToken"     : self.refreshToken,
            "refreshExpires"   : self.refreshExpires,
            "refreshExpiresAt" : self.refreshExpiresAt,
            "accountID"        : self.accountID,
            "clientID"         : self.clientID,
            "internalClient"   : self.internalClient,
            "clientService"    : self.clientService,
            "displayName"      : self.displayName,
            "app"              : self.app,
            "appID"            : self.appID
        }
    
    @classmethod
    def from_dict(cls, data:dict):
        return cls(
            data.get("access_token", ""),
            data.get("expires_in", 0),
            data.get("expires_at", ""),
            data.get("token_type"),
            data.get("refresh_token", ""),
            data.get("refresh_expires", ""),
            data.get("refresh_expires_at", ""),
            data.get("account_id", ""),
            data.get("client_id", ""),
            data.get("internal_client", False),
            data.get("client_service", ""),
            data.get("displayName", ""),
            data.get("app", ""),
            data.get("in_app_id", "")
        )
    
