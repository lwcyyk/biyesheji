// Generated verbatim declarations from Casdoor (Apache-2.0); see SOURCE_EXTRACTS.json.
package controllers
import object "policyreview.local/mockobject"

func (c *ApiController) SetSessionUsername(user string) {
	c.SetSession("username", user)
	c.clearSessionOidc()
}

func (c *ApiController) clearSessionOidc() {
	c.DelSession("scope")
	c.DelSession("aud")
	c.DelSession(object.SessionSigninTokenId)
}

