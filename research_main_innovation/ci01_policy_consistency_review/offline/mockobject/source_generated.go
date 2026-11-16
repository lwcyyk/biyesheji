// Generated verbatim declarations from Casdoor (Apache-2.0); see SOURCE_EXTRACTS.json.
package object
import ("fmt"; "strings"; util "policyreview.local/mockutil")

func (application *Application) IsDynamicClient() bool {
	return util.InSlice(application.Tags, "dcr") || util.InSlice(application.Tags, cimdTag)
}

func IsAppUser(userId string) bool {
	if strings.HasPrefix(userId, "app/") || strings.HasPrefix(userId, "app-dcr/") {
		return true
	}
	return false
}

const SessionSigninTokenId = "signinTokenId"

func (token *Token) GetId() string {
	return fmt.Sprintf("%s/%s", token.Owner, token.Name)
}

func (token *Token) IsUserActive() (bool, error) {
	if token.GrantType == "client_credentials" || token.User == "" {
		return true, nil
	}

	user, err := getUser(token.Organization, token.User)
	if err != nil {
		return false, err
	}
	if user == nil {
		return false, nil
	}

	return !user.IsForbidden && !user.IsDeleted, nil
}

