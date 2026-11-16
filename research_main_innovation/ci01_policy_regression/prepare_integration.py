"""Install I/O-only fixtures and observation probes, preserving policy bodies."""
from pathlib import Path
from hashlib import sha256
import json,shutil,difflib
ROOT=Path(__file__).resolve().parent
def main():
    src=ROOT/'baseline'
    if (ROOT/'OBSERVABILITY.diff').exists():raise RuntimeError('already installed')
    changes={};modified={}
    def edit(rel,old,new,count=1):
        p=src/rel
        if rel not in changes:changes[rel]=p.read_text(encoding='utf-8');modified[rel]=changes[rel]
        text=modified[rel]
        if text.count(old)!=count:raise RuntimeError(f'anchor {rel}: expected {count}, found {text.count(old)}')
        modified[rel]=text.replace(old,new)
    for rel in ['routers/authz_filter.go','routers/base.go','controllers/user.go','controllers/account.go','object/application.go','object/token.go']:
        edit(rel,'import (','import (\n\t"github.com/casdoor/casdoor/ci01audit"')
    edit('routers/authz_filter.go','if !checkDynamicClientSession(ctx, urlPath) {',
      'ci01Gate := checkDynamicClientSession(ctx, urlPath)\n\tci01audit.Record("client_gate_return", ci01Gate, getSessionUser(ctx))\n\tif !ci01Gate {')
    edit('routers/authz_filter.go','ctx.Input.SetData("currentUserId", username)',
      'ctx.Input.SetData("currentUserId", username)\n\tci01audit.Record("subject_identified", username != "", username)')
    edit('routers/authz_filter.go','allowed, err := authz.IsAllowed(subOwner, subName, method, urlPath, obj.Owner, obj.Name, extraInfo)',
      'ci01audit.Record("global_permission_enter", true, urlPath)\n\t\tallowed, err := authz.IsAllowed(subOwner, subName, method, urlPath, obj.Owner, obj.Name, extraInfo)\n\t\tci01audit.Record("global_permission_result", allowed && err == nil, urlPath)')
    edit('controllers/user.go','func (c *ApiController) UpdateUser() {',
      'func (c *ApiController) UpdateUser() {\n\tci01audit.Record("controller_enter", true, "UpdateUser")')
    edit('controllers/user.go','affected, err := object.UpdateUser(id, &user, columns, isAdmin)',
      'ci01audit.Record("controller_permission_pass", true, "UpdateUser")\n\taffected, err := object.UpdateUser(id, &user, columns, isAdmin)')
    edit('controllers/account.go','func (c *ApiController) GetUserinfo() {',
      'func (c *ApiController) GetUserinfo() {\n\tci01audit.Record("controller_enter", true, "GetUserinfo")')
    edit('controllers/account.go','scope, aud := c.GetSessionOidc()',
      'ci01audit.Record("controller_permission_pass", true, "userinfo_signed_in")\n\tscope, aud := c.GetSessionOidc()',count=1)
    # Narrow operation counts, independent of downstream audit SQL.
    edit('object/application.go','func GetApplicationByClientId(clientId string) (*Application, error) {',
      'func GetApplicationByClientId(clientId string) (*Application, error) {\n\tci01audit.Count("application_by_client_lookup")')
    edit('object/application.go','func GetApplicationByUserId(userId string) (application *Application, err error) {',
      'func GetApplicationByUserId(userId string) (application *Application, err error) {\n\tci01audit.Count("application_by_user_lookup")')
    edit('object/token.go','func GetToken(id string) (*Token, error) {','func GetToken(id string) (*Token, error) {\n\tci01audit.Count("source_token_id_lookup")')
    edit('routers/base.go','func clearSessionOfToken(ctx *context.Context) error {',
      'func clearSessionOfToken(ctx *context.Context) error {\n\tci01audit.Count("clear_source_identity_calls")')
    edit('routers/base.go','for _, key := range []string{"username", "SessionData", "accessToken", "scope", "aud", object.SessionSigninTokenId} {',
      'for _, key := range []string{"username", "SessionData", "accessToken", "scope", "aud", object.SessionSigninTokenId} {\n\t\tci01audit.Count("clear_source_delete_attempts")')
    diff=[]
    for rel,before in changes.items():
        after=modified[rel]
        saved=ROOT/'originals'/rel;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_text(before,encoding='utf-8',newline='\n')
        (src/rel).write_text(after,encoding='utf-8',newline='\n')
        diff.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
    (ROOT/'OBSERVABILITY.diff').write_text(''.join(diff),encoding='utf-8',newline='\n')
    for p in (ROOT/'harness').rglob('*'):
        if p.is_file():q=src/p.relative_to(ROOT/'harness');q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
    (ROOT/'INSTRUMENTATION_HASHES.json').write_text(json.dumps([{'path':rel,'before':sha256(before.encode()).hexdigest(),'after':sha256((src/rel).read_bytes()).hexdigest()} for rel,before in changes.items()],indent=2),encoding='utf-8')
    print('observation and fixture files installed; no correctness patch')
if __name__=='__main__':main()
