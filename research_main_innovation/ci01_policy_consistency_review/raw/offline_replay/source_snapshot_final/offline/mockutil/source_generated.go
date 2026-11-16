// Generated verbatim declarations from Casdoor (Apache-2.0); see SOURCE_EXTRACTS.json.
package util
import ("fmt"; "strings"; "time"; "errors")

func IsTokenExpired(createdTime string, expiresIn int) (bool, string) {
	createdTimeObj, _ := time.Parse(time.RFC3339, createdTime)
	expiresAtObj := createdTimeObj.Add(time.Duration(expiresIn) * time.Second)
	isExpired := time.Now().After(expiresAtObj)
	expireTime := expiresAtObj.Local().Format(time.RFC3339)
	return isExpired, expireTime
}

func GetId(owner, name string) string {
	return fmt.Sprintf("%s/%s", owner, name)
}

func GetOwnerAndNameFromIdNoCheck(id string) (string, string) {
	tokens := strings.SplitN(id, "/", 2)
	return tokens[0], tokens[1]
}

func GetOwnerAndNameFromIdWithError(id string) (string, string, error) {
	tokens := strings.Split(id, "/")
	if len(tokens) != 2 {
		return "", "", errors.New("GetOwnerAndNameFromId() error, wrong token count for ID: " + id)
	}

	return tokens[0], tokens[1], nil
}

